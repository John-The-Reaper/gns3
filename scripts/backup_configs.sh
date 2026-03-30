#!/bin/bash
# ============================================================
# TechNova - Sauvegarde des configurations GNS3
# Sauvegarde les configs running de tous les équipements réseau
# Usage: ./backup_configs.sh
# ============================================================

BACKUP_DIR="/home/faucheur/gns3/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG="$BACKUP_DIR/backup_$DATE.log"

mkdir -p "$BACKUP_DIR"

echo "=== TechNova Config Backup - $DATE ===" | tee "$LOG"

# Équipements Cisco IOS (telnet console)
declare -A CISCO_NODES=(
    ["RouterInternet"]="5211"
    ["L3Switch-1"]="5239"
    ["L3Switch-2"]="5247"
)

backup_cisco() {
    local name=$1
    local port=$2
    local outfile="$BACKUP_DIR/${name}_${DATE}.cfg"

    echo -n "  Backup $name (port $port)... " | tee -a "$LOG"

    # Récupère la running-config via telnet
    config=$(python3 -c "
import socket, time, sys
try:
    s = socket.socket()
    s.settimeout(15)
    s.connect(('192.168.212.175', $port))
    time.sleep(2)
    # drain
    try:
        while True: s.recv(4096)
    except: pass
    s.send(b'\r\n')
    time.sleep(2)
    # drain
    try:
        while True: s.recv(4096)
    except: pass
    s.send(b'enable\r\n')
    time.sleep(1)
    try:
        while True: s.recv(4096)
    except: pass
    s.send(b'terminal length 0\r\n')
    time.sleep(1)
    try:
        while True: s.recv(4096)
    except: pass
    s.send(b'show running-config\r\n')
    time.sleep(15)
    out = b''
    try:
        while True:
            d = s.recv(8192)
            if not d: break
            out += d
    except: pass
    s.close()
    # Extract config (between 'Building configuration' and end)
    text = out.decode('utf-8', errors='replace')
    start = text.find('Building configuration')
    if start == -1:
        start = text.find('Current configuration')
    if start != -1:
        print(text[start:])
    else:
        print(text)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)

    if echo "$config" | grep -q "ERROR"; then
        echo "ÉCHEC" | tee -a "$LOG"
        echo "  Erreur: $config" >> "$LOG"
        return 1
    fi

    echo "$config" > "$outfile"
    size=$(wc -c < "$outfile")
    echo "OK (${size} octets → $outfile)" | tee -a "$LOG"
    return 0
}

echo "" | tee -a "$LOG"
echo "--- Sauvegarde équipements Cisco IOS ---" | tee -a "$LOG"
success=0
fail=0

for name in "${!CISCO_NODES[@]}"; do
    if backup_cisco "$name" "${CISCO_NODES[$name]}"; then
        ((success++))
    else
        ((fail++))
    fi
done

echo "" | tee -a "$LOG"
echo "--- Résultat ---" | tee -a "$LOG"
echo "  Succès : $success" | tee -a "$LOG"
echo "  Échecs : $fail" | tee -a "$LOG"
echo "  Fichiers dans : $BACKUP_DIR" | tee -a "$LOG"

# Nettoyage : garder seulement les 10 dernières sauvegardes par nœud
echo "" | tee -a "$LOG"
echo "--- Nettoyage (>10 sauvegardes par nœud) ---" | tee -a "$LOG"
for name in "${!CISCO_NODES[@]}"; do
    count=$(ls "$BACKUP_DIR/${name}_"*.cfg 2>/dev/null | wc -l)
    if [ "$count" -gt 10 ]; then
        ls -t "$BACKUP_DIR/${name}_"*.cfg | tail -n +11 | xargs rm -f
        echo "  $name : suppression de $((count-10)) ancienne(s) sauvegarde(s)" | tee -a "$LOG"
    fi
done

echo "" | tee -a "$LOG"
echo "=== Backup terminé : $DATE ===" | tee -a "$LOG"

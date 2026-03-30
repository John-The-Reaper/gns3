#!/bin/bash
# ============================================================
# TechNova - Monitoring de connectivité réseau
# Vérifie la disponibilité des équipements et de l'accès internet
# Usage: ./monitor_ping.sh [--loop] [--interval 60]
# ============================================================

LOG_DIR="/home/faucheur/gns3/logs"
mkdir -p "$LOG_DIR"

LOOP=false
INTERVAL=60

# Parsing args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --loop) LOOP=true ;;
        --interval) INTERVAL="$2"; shift ;;
    esac
    shift
done

# Cibles de monitoring
declare -A TARGETS=(
    # Infrastructure
    ["RouterInternet-Gi4"]="10.0.15.1"
    ["RouterInternet-Gi2-NAT"]="192.168.42.130"
    ["L3Switch-1-Gi1-3"]="10.0.15.2"
    ["L3Switch-1-Gi0-0"]="10.0.16.1"
    ["L3Switch-2-Gi0-0"]="10.0.16.2"
    # Gateways VLAN Siège (HSRP virtual IPs)
    ["GW-VLAN10-RD"]="172.16.10.1"
    ["GW-VLAN20-RH"]="172.16.20.1"
    ["GW-VLAN30-Finance"]="172.16.30.1"
    ["GW-VLAN40-Juridique"]="172.16.40.1"
    # Internet
    ["Internet-Google"]="8.8.8.8"
    ["Internet-Cloudflare"]="1.1.1.1"
)

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_host() {
    local name=$1
    local ip=$2
    # Ping avec 2 paquets, timeout 2s
    if ping -c 2 -W 2 "$ip" > /dev/null 2>&1; then
        rtt=$(ping -c 2 -W 2 "$ip" 2>/dev/null | tail -1 | awk -F'/' '{print $5}' | cut -d'.' -f1)
        echo -e "  ${GREEN}[OK]${NC}   ${name} (${ip}) - RTT: ${rtt}ms"
        return 0
    else
        echo -e "  ${RED}[FAIL]${NC} ${name} (${ip}) - INJOIGNABLE"
        return 1
    fi
}

run_check() {
    local ts=$(date '+%Y-%m-%d %H:%M:%S')
    local logfile="$LOG_DIR/ping_$(date +%Y%m%d).log"

    echo ""
    echo "================================================="
    echo " TechNova Network Monitor - $ts"
    echo "================================================="

    total=0
    ok=0
    fail=0
    results=""

    for name in "${!TARGETS[@]}"; do
        ip="${TARGETS[$name]}"
        ((total++))
        output=$(check_host "$name" "$ip")
        echo "$output"
        if echo "$output" | grep -q "\[OK\]"; then
            ((ok++))
            results+="OK,$name,$ip\n"
        else
            ((fail++))
            results+="FAIL,$name,$ip\n"
        fi
    done

    echo ""
    echo "--- Résumé : $ok/$total disponibles ---"
    if [ "$fail" -gt 0 ]; then
        echo -e "  ${RED}⚠ $fail équipement(s) injoignable(s)${NC}"
    else
        echo -e "  ${GREEN}✓ Tout est opérationnel${NC}"
    fi

    # Log CSV
    echo "# Check: $ts" >> "$logfile"
    echo -e "$results" >> "$logfile"
}

if $LOOP; then
    echo "Mode surveillance continue (intervalle: ${INTERVAL}s). Ctrl+C pour arrêter."
    while true; do
        run_check
        sleep "$INTERVAL"
    done
else
    run_check
fi

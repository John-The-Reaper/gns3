#!/usr/bin/env python3
"""
TechNova - Configuration complète Switch-L3-1 et L3Switch-2
Exécuter: python3 configure_switches.py
"""
import socket, time, sys

HOST = '192.168.212.175'
SW1_PORT = 5239  # Switch-L3-1
SW2_PORT = 5247  # L3Switch-2


def make_conn(host, port, name):
    print(f"\n{'='*50}")
    print(f"Connexion à {name} ({host}:{port})...")
    s = socket.socket()
    s.settimeout(5)
    s.connect((host, port))
    time.sleep(2)
    try: s.recv(8192)
    except: pass
    print(f"  Connecté.")
    return s


def send_cmd(s, cmd, wait=0.4):
    s.send((cmd + '\r\n').encode())
    time.sleep(wait)
    out = b''
    s.settimeout(1.5)
    try:
        while True:
            chunk = s.recv(8192)
            if not chunk:
                break
            out += chunk
    except:
        pass
    return out.decode(errors='ignore')


def configure(s, cmds, section=""):
    print(f"  --- {section} ---")
    send_cmd(s, '', 0.3)
    send_cmd(s, 'enable', 0.5)
    send_cmd(s, 'terminal length 0', 0.3)
    send_cmd(s, 'conf t', 0.5)
    for cmd in cmds:
        resp = send_cmd(s, cmd, 0.3)
        if '%' in resp:
            clean = resp.replace('\r', '').replace('\n', ' ')
            for part in clean.split('%'):
                if part.strip():
                    print(f"    WARN: %{part.strip()[:80]}")
    send_cmd(s, 'end', 0.5)
    print(f"    Sauvegarde...", end='', flush=True)
    resp = send_cmd(s, 'write memory', 6)
    if 'OK' in resp or 'Building' in resp:
        print(" OK ✓")
    else:
        print(f" (vérifier manuellement)")
    print(f"  --- {section} terminé ---")


# ================================================================
# SWITCH-L3-1
# ================================================================
s1 = make_conn(HOST, SW1_PORT, 'Switch-L3-1')

configure(s1, [
    # Routage L3
    "ip routing",

    # VLANs Paris
    "vlan 60", "name LOGISTIQUE", "exit",
    "vlan 70", "name PRODUCTION", "exit",
    "vlan 80", "name QUALITE",    "exit",
    "vlan 90", "name MARKETING",  "exit",

    # SVI VLAN 30 — Finance Siège
    "interface Vlan30",
    "ip address 172.16.30.2 255.255.255.0",
    "standby 30 ip 172.16.30.1",
    "standby 30 priority 110",
    "standby 30 preempt",
    "no shutdown", "exit",

    # SVI VLAN 40 — Juridique Siège
    "interface Vlan40",
    "ip address 172.16.40.2 255.255.255.0",
    "standby 40 ip 172.16.40.1",
    "standby 40 priority 110",
    "standby 40 preempt",
    "no shutdown", "exit",

    # SVI VLAN 50 — Serveurs (activer)
    "interface Vlan50",
    "standby 50 priority 110",
    "standby 50 preempt",
    "no shutdown", "exit",

    # SVI VLAN 60 — Logistique Paris
    "interface Vlan60",
    "ip address 172.16.60.2 255.255.255.0",
    "standby 60 ip 172.16.60.1",
    "standby 60 priority 110",
    "standby 60 preempt",
    "no shutdown", "exit",

    # SVI VLAN 70 — Production Paris
    "interface Vlan70",
    "ip address 172.16.70.2 255.255.255.0",
    "standby 70 ip 172.16.70.1",
    "standby 70 priority 110",
    "standby 70 preempt",
    "no shutdown", "exit",

    # SVI VLAN 80 — Qualité Paris
    "interface Vlan80",
    "ip address 172.16.80.2 255.255.255.0",
    "standby 80 ip 172.16.80.1",
    "standby 80 priority 110",
    "standby 80 preempt",
    "no shutdown", "exit",

    # SVI VLAN 90 — Marketing Paris
    "interface Vlan90",
    "ip address 172.16.90.2 255.255.255.0",
    "standby 90 ip 172.16.90.1",
    "standby 90 priority 110",
    "standby 90 preempt",
    "no shutdown", "exit",

    # SVI VLAN 99 — Management
    "interface Vlan99",
    "ip address 172.16.99.2 255.255.255.0",
    "standby 99 ip 172.16.99.1",
    "standby 99 priority 110",
    "standby 99 preempt",
    "no shutdown", "exit",

    # DHCP — exclusions nouvelles VLANs
    "ip dhcp excluded-address 172.16.30.1 172.16.30.9",
    "ip dhcp excluded-address 172.16.40.1 172.16.40.9",
    "ip dhcp excluded-address 192.168.50.1 192.168.50.9",
    "ip dhcp excluded-address 172.16.60.1 172.16.60.9",
    "ip dhcp excluded-address 172.16.70.1 172.16.70.9",
    "ip dhcp excluded-address 172.16.80.1 172.16.80.9",
    "ip dhcp excluded-address 172.16.90.1 172.16.90.9",
    "ip dhcp excluded-address 172.16.99.1 172.16.99.19",

    # DHCP — mise à jour pools VLAN 10 & 20 (DNS interne)
    "ip dhcp pool VLAN10",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "exit",

    "ip dhcp pool VLAN20",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "exit",

    # DHCP — nouveaux pools
    "ip dhcp pool VLAN30",
    "network 172.16.30.0 255.255.255.0",
    "default-router 172.16.30.1",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "lease 1", "exit",

    "ip dhcp pool VLAN40",
    "network 172.16.40.0 255.255.255.0",
    "default-router 172.16.40.1",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "lease 1", "exit",

    "ip dhcp pool VLAN50",
    "network 192.168.50.0 255.255.255.0",
    "default-router 192.168.50.1",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "lease 1", "exit",

    "ip dhcp pool VLAN60",
    "network 172.16.60.0 255.255.255.0",
    "default-router 172.16.60.1",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "lease 1", "exit",

    "ip dhcp pool VLAN70",
    "network 172.16.70.0 255.255.255.0",
    "default-router 172.16.70.1",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "lease 1", "exit",

    "ip dhcp pool VLAN80",
    "network 172.16.80.0 255.255.255.0",
    "default-router 172.16.80.1",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "lease 1", "exit",

    "ip dhcp pool VLAN90",
    "network 172.16.90.0 255.255.255.0",
    "default-router 172.16.90.1",
    "dns-server 172.16.99.1",
    "domain-name technova.local",
    "lease 1", "exit",

    # DNS serveur IOS
    "ip dns server",
    "ip domain-name technova.local",
    "ip name-server 8.8.8.8",
    "ip host sw-l3-1.technova.local 172.16.99.2",
    "ip host sw-l3-2.technova.local 172.16.99.3",

], "Switch-L3-1 — VLANs+SVIs+HSRP+DHCP+DNS")

s1.close()

# ================================================================
# L3SWITCH-2
# ================================================================
time.sleep(2)
s2 = make_conn(HOST, SW2_PORT, 'L3Switch-2')

configure(s2, [
    "ip routing",

    # VLANs (tous)
    "vlan 10", "name RD",         "exit",
    "vlan 20", "name RH",         "exit",
    "vlan 30", "name FINANCE",    "exit",
    "vlan 40", "name JURIDIQUE",  "exit",
    "vlan 50", "name SERVEURS",   "exit",
    "vlan 60", "name LOGISTIQUE", "exit",
    "vlan 70", "name PRODUCTION", "exit",
    "vlan 80", "name QUALITE",    "exit",
    "vlan 90", "name MARKETING",  "exit",
    "vlan 99", "name MANAGEMENT", "exit",

    # SVI VLAN 10 (déjà 172.16.10.3)
    "interface Vlan10",
    "no shutdown", "exit",

    # SVI VLAN 20
    "interface Vlan20",
    "ip address 172.16.20.3 255.255.255.0",
    "standby 20 ip 172.16.20.1",
    "no shutdown", "exit",

    # SVI VLAN 30
    "interface Vlan30",
    "ip address 172.16.30.3 255.255.255.0",
    "standby 30 ip 172.16.30.1",
    "no shutdown", "exit",

    # SVI VLAN 40
    "interface Vlan40",
    "ip address 172.16.40.3 255.255.255.0",
    "standby 40 ip 172.16.40.1",
    "no shutdown", "exit",

    # SVI VLAN 50 (déjà 192.168.50.2)
    "interface Vlan50",
    "no shutdown", "exit",

    # SVI VLAN 60
    "interface Vlan60",
    "ip address 172.16.60.3 255.255.255.0",
    "standby 60 ip 172.16.60.1",
    "no shutdown", "exit",

    # SVI VLAN 70
    "interface Vlan70",
    "ip address 172.16.70.3 255.255.255.0",
    "standby 70 ip 172.16.70.1",
    "no shutdown", "exit",

    # SVI VLAN 80
    "interface Vlan80",
    "ip address 172.16.80.3 255.255.255.0",
    "standby 80 ip 172.16.80.1",
    "no shutdown", "exit",

    # SVI VLAN 90
    "interface Vlan90",
    "ip address 172.16.90.3 255.255.255.0",
    "standby 90 ip 172.16.90.1",
    "no shutdown", "exit",

    # SVI VLAN 99
    "interface Vlan99",
    "ip address 172.16.99.3 255.255.255.0",
    "standby 99 ip 172.16.99.1",
    "no shutdown", "exit",

], "L3Switch-2 — VLANs+SVIs+HSRP")

s2.close()
print("\n\nConfiguration terminée. Relance avec: python3 configure_switches.py")

import socket
import subprocess


def get_current_ip():
    try:
        # Try hostname -I to get all IPs
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        ips = result.stdout.strip().split()
        for ip in ips:
            if not ip.startswith("127."):
                return ip

        # Fallback to socket method if hostname -I fails
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_current_ssid():
    try:
        # Get active connection using nmcli
        result = subprocess.run(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        for line in result.stdout.strip().split("\n"):
            if line.startswith("yes:"):
                ssid = line.split("yes:")[1]
                if ssid:
                    return ssid
        return ""
    except Exception:
        return ""


def scan_wifi():
    try:
        # Use nmcli to scan wifi
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL", "device", "wifi", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        networks = []
        seen = set()
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split(":")
                if len(parts) >= 2:
                    ssid = parts[0]
                    # Filter escape sequences added by nmcli for colons etc if any, but usually plain string
                    if ssid and ssid != "--" and ssid not in seen:
                        networks.append({"ssid": ssid, "signal": parts[1]})
                        seen.add(ssid)
        return networks
    except Exception:
        return [{"ssid": "Gagal memindai (nmcli tidak tersedia)", "signal": "0"}]


def connect_wifi(ssid, password):
    try:
        if get_current_ssid() == ssid:
            return True, "Sudah terhubung ke jaringan ini!"

        if password:
            result = subprocess.run(
                ["nmcli", "device", "wifi", "connect", ssid, "password", password],
                capture_output=True,
                text=True,
                timeout=30,
            )
        else:
            result = subprocess.run(
                ["nmcli", "device", "wifi", "connect", ssid],
                capture_output=True,
                text=True,
                timeout=30,
            )

        if result.returncode == 0:
            return True, "Berhasil terhubung!"
        else:
            return False, result.stderr or result.stdout
    except Exception as e:
        return False, str(e)

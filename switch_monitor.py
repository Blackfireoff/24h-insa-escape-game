import telnetlib
import time
import subprocess

# Config
HOST = "192.168.0.1"
PASSWORD = "R00tR00t"
ENABLE_PASSWORD = "adminenable"
PORTS_TO_CHECK = [4, 6, 10, 12, 14, 17, 20, 24]
SOUND_PATH = "success.mp3"
AUDIO_DEVICE = "hw:1,0"  # à adapter selon ta sortie HDMI/JACK

def play_success_sound():
    try:
        subprocess.run(["mpg123", "-a", AUDIO_DEVICE, SOUND_PATH])
    except Exception as e:
        print(f"[ERREUR] Lecture MP3 échouée : {e}")

def login_telnet():
    try:
        tn = telnetlib.Telnet(HOST, timeout=10)
        tn.read_until(b"Password:")
        tn.write(PASSWORD.encode("ascii") + b"\n")
        tn.write(b"enable\n")
        tn.read_until(b"Password:")
        tn.write(ENABLE_PASSWORD.encode("ascii") + b"\n")
        tn.write(b"terminal length 0\n")
        return tn
    except Exception as e:
        print(f"[ERREUR] Connexion Telnet échouée : {e}")
        return None

def get_ports_status(tn):
    tn.write(b"show interfaces status\n")
    time.sleep(1)
    output = tn.read_very_eager().decode("utf-8")
    return output

def parse_ports(output):
    up_ports = set()
    for line in output.splitlines():
        for port in PORTS_TO_CHECK:
            if f"Fa0/{port}" in line and "connected" in line:
                up_ports.add(port)
    return up_ports

def main():
    print("[INFO] Connexion au switch...")
    tn = login_telnet()
    if not tn:
        return

    print("[INFO] Surveillance cyclique des ports : ", PORTS_TO_CHECK)
    alert_ready = True

    while True:
        try:
            output = get_ports_status(tn)
            current_up_ports = parse_ports(output)

            # Affichage des changements
            for port in PORTS_TO_CHECK:
                if port in current_up_ports:
                    print(f"[+] Port Fa0/{port} : connecté")
                else:
                    print(f"[-] Port Fa0/{port} : déconnecté")

            all_connected = all(port in current_up_ports for port in PORTS_TO_CHECK)
            all_disconnected = all(port not in current_up_ports for port in PORTS_TO_CHECK)

            if all_connected and alert_ready:
                print("✅ Tous les ports sont connectés ! 🎉")
                for i in range(3):
                    play_success_sound()
                    time.sleep(2)
                alert_ready = False  # On attend qu'ils soient tous débranchés pour rejouer

            elif all_disconnected and not alert_ready:
                print("🔁 Tous les ports ont été déconnectés, réinitialisation de l'alerte")
                alert_ready = True

            time.sleep(5)

        except EOFError:
            print("[ERREUR] Connexion Telnet interrompue. Reconnexion...")
            tn = login_telnet()
        except Exception as e:
            print(f"[ERREUR] Exception dans la boucle principale : {e}")
            break

    tn.close()

if __name__ == "__main__":
    main()

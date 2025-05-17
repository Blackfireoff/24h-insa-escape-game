import telnetlib
import time
from playsound import playsound

# Config
HOST = "192.168.0.1"
USERNAME = "admin"
PASSWORD = "R00tR00t"
ENABLE_PASSWORD = "adminenable"
PORTS_TO_CHECK = [4, 6, 10, 12, 14, 17, 20, 24]
SOUND_PATH = "success.wav"

# État des ports suivis
previous_up_ports = set()

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
    global previous_up_ports
    print("[INFO] Connexion au switch...")
    tn = login_telnet()

    if not tn:
        return

    print("[INFO] Surveillance des ports : ", PORTS_TO_CHECK)
    already_played = False

    while True:
        try:
            output = get_ports_status(tn)
            current_up_ports = parse_ports(output)

            for port in PORTS_TO_CHECK:
                if port in current_up_ports and port not in previous_up_ports:
                    print(f"[+] Port Fa0/{port} connecté !")
                elif port not in current_up_ports and port in previous_up_ports:
                    print(f"[-] Port Fa0/{port} déconnecté.")

            previous_up_ports = current_up_ports

            if all(port in current_up_ports for port in PORTS_TO_CHECK):
                if not already_played:
                    print("✅ Tous les ports sont connectés ! 🎉")
                    playsound(SOUND_PATH)
                    already_played = True
            else:
                already_played = False

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

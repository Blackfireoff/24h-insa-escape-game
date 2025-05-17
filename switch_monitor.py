import telnetlib
import time
from playsound import playsound

# Configuration
HOST = "192.168.0.1"
USERNAME = "admin"
PASSWORD = "R00tR00t"
ENABLE_PASSWORD = "adminenable"
PORTS_TO_CHECK = [4, 6, 10, 12, 14, 17, 20, 24]
SOUND_PATH = "success.wav"

def is_all_ports_up(output):
    up_ports = set()
    for line in output.splitlines():
        for port in PORTS_TO_CHECK:
            port_name = f"FastEthernet0/{port}"
            if port_name in line and "connected" in line:
                up_ports.add(port)
    return all(port in up_ports for port in PORTS_TO_CHECK)

def connect_and_check():
    try:
        tn = telnetlib.Telnet(HOST, timeout=5)

        tn.read_until(b"Username:")
        tn.write(USERNAME.encode('ascii') + b"\n")

        tn.read_until(b"Password:")
        tn.write(PASSWORD.encode('ascii') + b"\n")

        tn.write(b"enable\n")
        tn.read_until(b"Password:")
        tn.write(ENABLE_PASSWORD.encode('ascii') + b"\n")

        tn.write(b"terminal length 0\n")
        tn.write(b"show interfaces status\n")
        tn.write(b"exit\n")

        output = tn.read_all().decode("utf-8")
        tn.close()

        return output

    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return ""

def main():
    print("🔍 Surveillance des ports en cours...")
    already_triggered = False

    while True:
        output = connect_and_check()
        if output:
            if is_all_ports_up(output):
                if not already_triggered:
                    print("✅ Tous les ports sont connectés !")
                    playsound(SOUND_PATH)
                    already_triggered = True
            else:
                already_triggered = False
        time.sleep(5)  # pause entre chaque check

if __name__ == "__main__":
    main()

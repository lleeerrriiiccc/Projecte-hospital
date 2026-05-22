import os
import socket
import subprocess
import sys
import time

from dotenv import load_dotenv


def _load_environment():
	load_dotenv()
	load_dotenv(os.path.join("server", ".env"), override=True)


def _wait_for_server(host, port, timeout=30):
	deadline = time.time() + timeout
	while time.time() < deadline:
		try:
			with socket.create_connection((host, port), timeout=1):
				return True
		except OSError:
			time.sleep(0.25)
	return False


_load_environment()

host = os.getenv("FLASK_HOST", "127.0.0.1")
port = int(os.getenv("FLASK_PORT", "5000"))

# Engeguem el servidor Flask en segon pla
print("Iniciant el servidor...")
servidor = subprocess.Popen([sys.executable, "main.py"], cwd="server")

if not _wait_for_server(host, port):
	servidor.terminate()
	raise RuntimeError(f"El servidor Flask no ha respost a {host}:{port}.")

# Engeguem el client d'escriptori i esperem que l'usuari el tanqui
print("Iniciant el client...")
subprocess.run([sys.executable, "desktop_main.py"], cwd="client")

# Quan el client es tanca, aturem el servidor
print("Aturant el servidor...")
servidor.terminate()

import subprocess
import sys

# Engeguem el servidor Flask en segon pla
print("Iniciant el servidor...")
servidor = subprocess.Popen([sys.executable, "server/main.py"])

# Engeguem el client d'escriptori i esperem que l'usuari el tanqui
print("Iniciant el client...")
subprocess.run([sys.executable, "client/desktop_main.py"])

# Quan el client es tanca, aturem el servidor
print("Aturant el servidor...")
servidor.terminate()

import sys
import os
import json
import serial
import time
import threading
import webview
import pkgutil
from importlib import resources


def base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def salir(msg, code=0):
    print(msg)

def init_serial():
    global ser
    ser_cfg = cfg["serial"]

    print(f"Abriendo puerto {ser_cfg['port']}...")

    try:
        ser = serial.Serial(
            port=ser_cfg["port"],
            baudrate=ser_cfg["baudrate"],
            bytesize=ser_cfg["bytesize"],
            parity={
                "N": serial.PARITY_NONE,
                "E": serial.PARITY_EVEN,
                "O": serial.PARITY_ODD
            }[ser_cfg["parity"]],
            stopbits=ser_cfg["stopbits"],
            timeout=0.5  # 500 ms
        )
    except Exception as e:
        salir(f"No se pudo abrir el puerto: {e}", 2)

    print("Dispositivo hallado")

def enviar(indice):
    global ser
    global tespera
    
    cmd = f"A{indice}\r"
    
    print(f" Tiempo: '{tespera}' | Indice abierto: '{cmd}'")
    if not ser or not ser.is_open:
        print("Puerto no inicializado")
        return

    print(f"Enviando: {cmd.strip()}")

    ser.write(cmd.encode())

    time.sleep(tespera)

    raw = ser.readline()
    texto = raw.decode(errors="ignore").strip()

    print(f"Respuesta recibida -> '{texto}'")
    return texto


def cerrar_serial():
    if ser and ser.is_open:
        ser.close()
        print("Puerto cerrado")
        
  
config_path = os.path.join(base_path(), "config.json")

try:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
except Exception as e:
    print(f"No se encontró config.json en:\n{config_path} \r")
    sys.exit(1)

ser = None  # 👈 referencia global controlada
tespera = cfg["serial"]["waittime"]

class Api:
    def cerrar(self):
        print("Cerrando aplicación...")
        os._exit(0)
    def enviar(self, indice):
        print(f"Enviar {indice}")
        return enviar(indice)   # llama a tu función real

    
def start_webview():
    html_path = os.path.join(base_path(), "ui", "index.html")

    webview.create_window(
        "Vending Monitor",
        html_path,
        fullscreen=True,
        js_api=Api()
    )
    webview.start()
    
def run_serial():
    init_serial()

def launch_serial():
    t = threading.Thread(target=run_serial, daemon=True)
    t.start()

if __name__ == "__main__":
    launch_serial()   # 🔌 serial en paralelo
    start_webview()   # 🖥️ webview en el MAIN THREAD

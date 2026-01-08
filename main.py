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
import serial

ser = []  # lista global

def init_serial():
    global ser
    ser = []

    ser_cfg = cfg["serial"]

    for i, port in enumerate(ser_cfg["ports"]):
        try:
            print(f"Abriendo puerto {port}...")

            s = serial.Serial(
                port=port,
                baudrate=ser_cfg["baudrate"],
                bytesize=ser_cfg["bytesize"],
                parity={
                    "N": serial.PARITY_NONE,
                    "E": serial.PARITY_EVEN,
                    "O": serial.PARITY_ODD
                }[ser_cfg["parity"]],
                stopbits=ser_cfg["stopbits"],
                timeout=ser_cfg.get("timeout", 0.5)
            )

            ser.append(s)

        except Exception as e:
            salir(f"No se pudo abrir {port}: {e}", 2)



def enviar(indice):
    global ser
    global tespera
    
    print("SER FINAL:")
    for i, s in enumerate(ser):
        print(i, s)


    indice = int(indice)
    ser_index = (indice - 1) // 4
    pos = 5-((indice - 1) % 4)
    
    print(f"Tiempo: {tespera} | Indice abierto: A{pos} | Puerto: {ser_index}")

    if ser_index >= len(ser):
        print(f"No existe ser[{ser_index}] para indice {pos}")
        return "ERROR"

    puerto = ser[ser_index]

    cmd = f"A{pos:02d}{chr(10)}"
    
    if not puerto or not puerto.is_open:
        print("Puerto no inicializado")
        time.sleep(tespera)
        return "OK"

    print(f"Enviando: {cmd.strip()}")
    puerto.write(cmd.encode())

    time.sleep(tespera)

    raw = puerto.readline()
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
    #webview.start(debug=True,args=["--disable-gpu","--disable-software-rasterizer","--autoplay-policy=no-user-gesture-required"])
    webview.start()
    
def run_serial():
    init_serial()

def launch_serial():
    t = threading.Thread(target=run_serial, daemon=True)
    t.start()

if __name__ == "__main__":
    launch_serial()   # 🔌 serial en paralelo
    start_webview()   # 🖥️ webview en el MAIN THREAD
    
input("cierre")
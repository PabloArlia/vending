import sys
import os
import json
import serial
import time


def base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def salir(msg, code=0):
    print(msg)
    input("\nPresione ENTER para salir...")
    sys.exit(code)


config_path = os.path.join(base_path(), "config.json")

try:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
except Exception as e:
    print(f"No se encontró config.json en:\n{config_path}")
    input("ENTER para salir...")
    sys.exit(1)

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

time.sleep(2)

cmd = cfg["commands"]["status"]
print(f"Enviando: {cmd.strip()}")

try:
    ser.write(cmd.encode())
except Exception as e:
    ser.close()
    salir(f"Error enviando comando: {e}", 3)

print("Esperando respuesta (5 intentos, 500 ms cada uno)...")

respuesta = ""
intentos = 5

for i in range(1, intentos + 1):
    try:
        raw = ser.readline()
        texto = raw.decode(errors="ignore").strip()

        if texto:
            print(f"Intento {i}: respuesta recibida -> '{texto}'")
            respuesta = texto
            break
        else:
            print(f"Intento {i}: sin respuesta")
    except Exception as e:
        print(f"Intento {i}: error leyendo -> {e}")

ser.close()

if not respuesta:
    salir("No hubo respuesta del dispositivo tras 5 intentos", 5)

mensaje = cfg["responses"].get(respuesta, "Código desconocido")

print(f"Respuesta final: {respuesta}")
print(f"Estado: {mensaje}")

salir("Proceso finalizado")

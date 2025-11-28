# Caso não tenha o brew instalado, rode no terminal: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Posteriormente, rode o braw: brew install socat
# Abrir um terminal e colocar: socat -d -d pty,raw,echo=0 pty,raw,echo=0
# Irá gerar as portas seriais de teste, pegar o primeiro endereço retornado (Ex: /dev/ttys036) e colocar
# no "porta_simulada".
# A segunda porta retornada (Ex: /dev/ttys037) inserie no App.py em "arduino".


import serial
import time

porta_simulada = 'dev/cu.usbserial-1420'  # Altere para a primeira porta exibida pelo socat

ser = serial.Serial(porta_simulada, 9600)

try:
    while True:
        temperatura_fake = '25.50\n'
        ser.write(temperatura_fake.encode('utf-8'))
        print(f"Enviado: {temperatura_fake.strip()}")
        time.sleep(1)
except KeyboardInterrupt:
    ser.close()
    print("Encerrado.")

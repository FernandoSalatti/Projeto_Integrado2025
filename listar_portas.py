import serial.tools.list_ports

def listar_portas():
    portas = serial.tools.list_ports.comports()
    if not portas:
        print("Nenhuma porta serial encontrada.")
    else:
        print("Portas seriais disponíveis:")
        for porta in portas:
            print(f"- {porta.device} | {porta.description}")

if __name__ == '__main__':
    listar_portas()

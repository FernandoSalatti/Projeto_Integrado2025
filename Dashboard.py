import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import threading
import time
import csv
import paho.mqtt.client as mqtt
from matplotlib.ticker import FuncFormatter  # Import para formatar ticks

# ----------------- CONFIGURAÇÕES DO MQTT -----------------
BROKER = "broker.hivemq.com"
TOPIC = "TrabalhoGB_Unisinos_Instrumentacao_2025_1"
PORT = 1883
CLIENT_ID = "ESP32_TEST"

class AnemometroDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard - Anemômetro MQTT")
        self.root.attributes('-fullscreen', True)  # Tela cheia no macOS
        self.fullscreen = True

        # Estilo dos botões com fundo preto
        style = ttk.Style()
        style.theme_use('clam')  # Mais compatível com customização
        style.configure("Black.TButton", background="black", foreground="white")

        # Dados
        self.medicoes = []
        self.tempo = []
        self.last_10 = deque(maxlen=10)
        self.max_v = None
        self.min_v = None
        self.start_time = time.time()
        self.mqtt_client = None
        self.after_id = None

        # ----- Layout principal (vertical) -----
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Frame do gráfico (topo)
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(side="top", fill="both", expand=False, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(6, 3))  # Gráfico com tamanho controlado
        self.line, = self.ax.plot([], [], color='blue')
        self.ax.set_title("Velocidade do Vento x Tempo")

        # Configura labels com unidades
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Velocidade (m/s)")

        # Ajuste do layout para evitar corte dos labels
        self.fig.tight_layout()

        # Opcional: formatar ticks para deixar mais legível (só números simples, pois unidades já estão no label)
        def y_fmt(x, pos):
            return f"{x:.1f}"

        def x_fmt(x, pos):
            return f"{x:.0f}"

        self.ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
        self.ax.xaxis.set_major_formatter(FuncFormatter(x_fmt))

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas_widget.config(width=800, height=500)

        # Frame das informações (meio)
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side="top", fill="x", padx=10)

        self.label_atual = ttk.Label(info_frame, text="Velocidade atual: -- m/s", font=("Arial", 22))
        self.label_atual.pack(anchor="w", pady=2)

        self.label_max = ttk.Label(info_frame, text="Máxima: -- m/s", font=("Arial", 20))
        self.label_max.pack(anchor="w", pady=2)

        self.label_min = ttk.Label(info_frame, text="Mínima: -- m/s", font=("Arial", 20))
        self.label_min.pack(anchor="w", pady=2)

        self.label_ultimos = ttk.Label(info_frame, text="Últimos 10 valores: --", font=("Arial", 20), wraplength=1000)
        self.label_ultimos.pack(anchor="w", pady=2)

        # Frame dos botões (base)
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(side="bottom", pady=20)

        self.botao_resetar = ttk.Button(botoes_frame, text="Resetar", style="Black.TButton", command=self.resetar)
        self.botao_resetar.grid(row=0, column=0, padx=10)

        self.botao_exportar = ttk.Button(botoes_frame, text="Exportar CSV", style="Black.TButton", command=self.exportar_csv)
        self.botao_exportar.grid(row=0, column=1, padx=10)

        self.botao_encerrar = ttk.Button(botoes_frame, text="Encerrar", style="Black.TButton", command=self.fechar_aplicacao)
        self.botao_encerrar.grid(row=0, column=2, padx=10)

        self.botao_tela_cheia = ttk.Button(botoes_frame, text="Alternar Tela Cheia", style="Black.TButton", command=self.toggle_fullscreen)
        self.botao_tela_cheia.grid(row=0, column=3, padx=10)

        # Captura fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)

        threading.Thread(target=self.iniciar_mqtt, daemon=True).start()
        self.atualizar_grafico()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def atualizar_grafico(self):
        self.line.set_data(self.tempo, self.medicoes)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.after_id = self.root.after(1000, self.atualizar_grafico)

    def on_mqtt_message(self, client, userdata, msg):
        try:
            valor = float(msg.payload.decode())
        except ValueError:
            print(f"Valor inválido recebido: {msg.payload}")
            return

        t = time.time() - self.start_time
        self.medicoes.append(valor)
        self.tempo.append(t)
        self.last_10.append(valor)

        if self.max_v is None or valor > self.max_v:
            self.max_v = valor
        if self.min_v is None or valor < self.min_v:
            self.min_v = valor

        self.label_atual.config(text=f"Velocidade atual: {valor:.2f} m/s")
        self.label_max.config(text=f"Máxima: {self.max_v:.2f} m/s")
        self.label_min.config(text=f"Mínima: {self.min_v:.2f} m/s")
        self.label_ultimos.config(text=f"Últimos 10 valores: {list(self.last_10)}")

    def iniciar_mqtt(self):
        client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.mqtt_client = client

        try:
            print("Conectando ao MQTT...")
            client.connect(BROKER, PORT, 60)
            print("Conectado ao broker MQTT.")
        except Exception as e:
            print(f"Erro ao conectar ao MQTT: {e}")
            return

        client.subscribe(TOPIC)
        client.on_message = self.on_mqtt_message
        client.loop_forever()

    def resetar(self):
        self.medicoes.clear()
        self.tempo.clear()
        self.last_10.clear()
        self.max_v = None
        self.min_v = None
        self.start_time = time.time()
        self.label_atual.config(text="Velocidade atual: -- m/s")
        self.label_max.config(text="Máxima: -- m/s")
        self.label_min.config(text="Mínima: -- m/s")
        self.label_ultimos.config(text="Últimos 10 valores: --")

    def exportar_csv(self):
        if not self.medicoes:
            messagebox.showwarning("Exportar CSV", "Nenhum dado para exportar.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Salvar dados como"
        )
        if filename:
            try:
                with open(filename, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Tempo (s)", "Velocidade (m/s)"])
                    writer.writerows(zip(self.tempo, self.medicoes))
                messagebox.showinfo("Exportar CSV", "Dados exportados com sucesso.")
            except Exception as e:
                messagebox.showerror("Exportar CSV", f"Erro ao salvar arquivo: {e}")

    def fechar_aplicacao(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                print("MQTT desconectado.")
            except Exception as e:
                print(f"Erro ao encerrar MQTT: {e}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnemometroDashboard(root)
    root.mainloop()

# 🌬️ Anemômetro com Dashboard MQTT em Tempo Real

Este projeto consiste em um **sistema de medição de velocidade do vento** utilizando um **anemômetro com sensor Hall**, desenvolvido com **Arduino**, e um **dashboard em Python** que recebe os dados em tempo real via **MQTT**.

## Integrantes
- André Comin
- Fernando Salatti

---

## Componentes do Projeto

### 1. `anemometro.ino` (Arduino)

Código-fonte para um anemômetro baseado em Arduino, que mede a velocidade do vento utilizando:

- Sensor Hall com disco e ímãs  
- Cálculo da velocidade do vento com base no tempo entre pulsos  
- Conversão entre m/s e km/h com botão físico  
- Exibição no display LCD 16x2  
- Envio de dados via Serial (para conexão com ESP32/MQTT)  

### 2. `dashboard.py` (Python)

Aplicação com interface gráfica feita em **Tkinter** e gráficos em **Matplotlib**, que:

- Conecta ao broker MQTT (`broker.hivemq.com`)  
- Recebe os dados do anemômetro publicados no tópico MQTT  
- Exibe a velocidade do vento em tempo real  
- Mostra valores mínimo, máximo e os últimos 10 registros  
- Permite exportar os dados para `.csv`  
- Suporte a tela cheia e reset do dashboard  

---

## 🔧 Scripts Adicionais para Testes

Para facilitar o desenvolvimento e validação do fluxo de dados entre **Serial → MQTT → Dashboard**, foram incluídos dois scripts auxiliares em Python.

---

### 3. `simulador_serial.py`

Script utilizado para **simular um dispositivo enviando dados via porta serial**, permitindo testar o dashboard e o fluxo MQTT mesmo sem o Arduino conectado.

Ele:

- Abre uma porta serial configurada manualmente  
- Envia continuamente um valor fake escolhido aleatoriamente
- Simula um sensor real enviando dados a cada 1 segundo  

#### Como usar:

1. Ajuste a porta serial no código:
   ```python
   porta_simulada = 'dev/cu.usbserial-1420'
2. Execute
   ```bash
   python simulador_serial.py
   ```
---

### 4. `listar_portas.py`

Script auxiliar para listar todas as portas seriais disponíveis no sistema.

### Como usar:

1. Execução
   ```bash
   python listar_portas.py
   ```
2. Exemplo de saída
   ```arduino
      Portas seriais disponíveis: - /dev/cu.usbserial-1420 | USB Serial Device
   ```
   
---

## Requisitos

### Para o Arduino:

- Arduino Uno ou compatível  
- Sensor Hall com disco e 4 ímãs  
- Display LCD 16x2  
- Botão para alternar entre m/s e km/h  
- Fonte de alimentação  
- (Opcional) ESP32 para publicar dados no MQTT  

### Para o Dashboard Python:

- Python 3.8 ou superior  
- Pacotes necessários:

```bash
pip install paho-mqtt matplotlib
```

## Como Usar

### No Arduino

- Monte o circuito com o sensor Hall, display LCD e botão.
- Faça upload do código anemometro.ino para seu Arduino.
- Se estiver usando ESP32 para MQTT, adapte o envio via Serial para publicação no tópico MQTT.

### No Python
- Execute o script do dashboard
```bash
python dashboard.py
```
- O painel abrirá em tela cheia e mostrará os dados recebidos via MQTT.

### Configuração MQTT
- Broker público: broker.hivemq.com
- Tópico MQTT: TrabalhoGB_Unisinos_Instrumentacao_2025_1 (você pode assinar para outro tópico, basta alterar no código do dashboard)
- Porta: 1883
- Client ID: ESP32_TEST
- O ESP32 (ou outro dispositivo) deve publicar os dados de velocidade como float no tópico acima (exemplo: 3.42)




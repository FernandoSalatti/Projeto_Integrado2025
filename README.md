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

#### 🧪 Testes do Módulo Arduino (`anemometro.ino`)

Os testes realizados no código do anemômetro foram realizados seguindo uma abordagem baseada no Modelo V.  
Incluem testes de unidade e de integração do módulo.

| ID | Tipo de Teste | Objetivo | Procedimento | Resultado Esperado |
|----|---------------|----------|--------------|---------------------|
| T-ARD-01 | Teste de Unidade | Validar cálculo da velocidade (m/s) | Simular um valor fixo de `intervalo` (ex.: 250000 µs). Forçar o cálculo da velocidade. | Velocidade ≈ 0,94 m/s (com erro aceitável). |
| T-ARD-02 | Teste de Unidade | Validar cálculo de RPM | Definir `media = 0.942` manualmente e calcular RPM. | RPM ≈ 60. |
| T-ARD-03 | Teste de Unidade | Verificar buffer circular e média móvel | Preencher mais de 10 valores seguidos (ex.: 15). Observar `indice`, `bufferCheio` e `media`. | `bufferCheio = true` após 10 valores; `media` reflete apenas os últimos 10. |
| T-ARD-04 | Teste de Unidade | Detectar vento parado | Sem pulsos por >3 s, observar valores adicionados ao buffer. | O buffer recebe valores `0.0`; `media` e `rpm` convergem para 0. |
| T-ARD-05 | Teste de Unidade | Validar condição `intervalo == 0` | Iniciar o sistema sem gerar pulsos e observar o comportamento. | O cálculo não deve ocorrer; nenhum valor inválido deve ser gerado. |
| T-ARD-06 | Teste de Robustez | Testar valores muito pequenos de `intervalo` | Forçar `intervalo = 1000 µs` e observar cálculos. | Arduino calcula sem travar; valores são coerentes matematicamente. |
| T-ARD-07 | Teste de Unidade | Validar alternância de unidade (m/s ↔ km/h) | Pressionar o botão (pino 3) repetidas vezes e observar `mostrarKMH`. | `mostrarKMH` alterna entre true/false a cada pressionamento. |
| T-ARD-08 | Teste de Integração | Validar escrita no LCD | Forçar valores conhecidos de `rpm` e observar o LCD. | Exibição correta: valor numérico + “RPM”; sem caracteres residuais. |
| T-ARD-09 | Teste de Integração | Validar leitura real do sensor Hall | Testar com diferentes rotações reais (baixa, média, alta). | `rpm` coerente com velocidade real dentro da precisão esperada. |
| T-ARD-10 | Teste de Integração | Validar periodicidade da atualização | Monitorar timestamps das leituras via Serial. | Atualizações a cada ~300 ms (+ processamento). |


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




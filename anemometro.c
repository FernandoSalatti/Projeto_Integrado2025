#include <LiquidCrystal.h>

// LCD: RS, E, D4, D5, D6, D7
LiquidCrystal lcd(12, 11, 5, 6, 7, 8);

#define hallPin 2         // Pino do sensor Hall
#define chavePin 3        // Chave para alternar km/h e m/s
#define numImas 4         // Número de ímãs no disco
#define bufferTamanho 10  // Número máximo de valores para a média

const float diametro = 0.30;   // Diâmetro do disco em metros


float velocidades[bufferTamanho];
byte indice = 0;
bool bufferCheio = false;

volatile unsigned long ultimoPulso = 0;
volatile unsigned long intervalo = 0;
volatile bool ventoParado = false;
volatile bool mostrarKMH = false;

void contarPulso()
{
  Serial.println("Imã detectado");
  unsigned long agora = micros();

  intervalo = agora - ultimoPulso;
  ultimoPulso = agora;
}

void unidadeVento()
{
  Serial.println("Botão pressionado");
  mostrarKMH = !mostrarKMH;
}

void setup()
{
  Serial.begin(9600);
  pinMode(hallPin, INPUT_PULLUP);
  pinMode(chavePin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(hallPin), contarPulso, FALLING);
  attachInterrupt(digitalPinToInterrupt(chavePin), unidadeVento, FALLING);

  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.print("Rot:");

  // Preenche o buffer inicial com zeros
  for (byte i = 0; i < bufferTamanho; i++)
  {
    velocidades[i] = 0.0;
  }
  Serial.println("Setup concluído");
}

void loop()
{
  unsigned long agora = micros();
  // Se passou muito tempo sem pulso, adiciona 0.0 no buffer
  if ((agora - ultimoPulso) > 3e6)
  {
    velocidades[indice] = 0.0;
    indice++;
    if (indice >= bufferTamanho)
    {
      indice = 0;
      bufferCheio = true;
    }
  }
  else if (intervalo > 0)
  {
    float velocidade = (3.1416 * diametro * 1e6) / (numImas * intervalo);

    velocidades[indice] = velocidade;
    indice++;
    if (indice >= bufferTamanho)
    {
      indice = 0;
      bufferCheio = true;
    }
  }

  // Calcula a média móvel
  float soma = 0;
  byte limite = bufferCheio ? bufferTamanho : indice;
  for (byte i = 0; i < limite; i++)
  {
    soma += velocidades[i];
  }
  float media = (limite > 0) ? (soma / limite) : 0;
  float rpm = (media * 60.0) / (3.1416 * diametro);
  Serial.println(rpm);

  // Verifica unidade de medida
  float mostrarVelocidade = media * (mostrarKMH ? 3.6 : 1.0);

  // Atualiza LCD com valor e unidade
  lcd.setCursor(0, 1);
  //lcd.print("Vel: ");
  lcd.print(rpm, 1);
  lcd.print("  ");
  lcd.setCursor(5, 1);
  //lcd.print(mostrarVelocidade, 2);
  //lcd.print(mostrarKMH ? " km/h " : " m/s  ");
  lcd.print("   RPM");

  delay(300); // Delay para suavizar a exibição
}

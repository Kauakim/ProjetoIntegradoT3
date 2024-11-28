#include <SPI.h>
#include <RF24.h>


int Sinal[750];
const char dado[] = "Telecom";
String Modo = "Taxa";

RF24 radio(9, 10);  // CE, CSN pinos
int CanalRadio = 8;  // Canal padrão do rádio


void setup() {
  // Inicia a serial
  Serial.begin(115200);

  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  
  // Inicia o modulo nRF24L01
  radio.begin();
  radio.stopListening();
}


void configurarModo(String Modo) {
  if (Modo == "Economia") {
    radio.setPALevel(RF24_PA_MIN);      // Potência mínima
    radio.setDataRate(RF24_1MBPS);      // Taxa de 1Mbps para baixo consumo de energia
  } 
  else if (Modo == "Taxa") {
    radio.setPALevel(RF24_PA_MAX);      // Potência máxima
    radio.setDataRate(RF24_2MBPS);      // Taxa de 2 Mbps para transmissão rápida
  } 
  else if (Modo == "Alcance") {
    radio.setPALevel(RF24_PA_MAX);      // Potência máxima para maior alcance
    radio.setDataRate(RF24_1MBPS);      // Taxa de 1 Mbps para maior alcance
  } 
  else {
    // Modo padrão (Taxa)
    radio.setDataRate(RF24_2MBPS);
    radio.setPALevel(RF24_PA_MAX);
  }
}


void loop() {
  // Coleta o sinal somado pelo circuito somador
  for (int i = 0; i <750; i++) {
    Sinal[i] = analogRead(A0);
    delayMicroseconds(1200);
  }
   
  // Envia o caractere "P" para indicar o início da transmissão
  Serial.println("P");
  delay(1000);
  
  // Envia os 500 valores
  for (int i = 0; i < 750; i++) {
    Serial.println(Sinal[i]);
    delayMicroseconds(500);
  }

  // Envia o caractere "F" para indicar o fim da transmissão
  Serial.println("F");
  delay(3000);


  // Aguarda a resposta da Raspberry Pi
  for (int i = 0; i < 10; i++) {
    char retorno1 = Serial.read();
    char retorno2 = Serial.read();

    if (retorno1 == 'R') {
      if (retorno2 == '1') {
        radio.setChannel(8);
      } else if (retorno2 == '2') {
        radio.setChannel(58);
      } else if (retorno2 == '3') {
        radio.setChannel(80);
      } else if (retorno2 == '4') {
        radio.setChannel(116);
      } else {
        return;
      }

      // Configura o modo e envia os dados
      configurarModo(Modo);
      for (int i = 0; i < 100; i++) {
        radio.write(&dado, sizeof(dado));
        delay(100);
      }
    }
    else {
      delay(100);
    }
  }
}

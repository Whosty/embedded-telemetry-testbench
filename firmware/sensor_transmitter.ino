const int BUTTON_PIN = 2;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  uint16_t sensor_val = analogRead(A0);
  uint8_t button_state = (digitalRead(BUTTON_PIN) == LOW) ? 1 : 0;

  uint8_t high_byte = (sensor_val >> 8) & 0xFF;
  uint8_t low_byte  = sensor_val & 0xFF;

  uint8_t paket[5];
  paket[0] = 0xAA;          // Başlangıç damgası (Header)
  paket[1] = high_byte;     // Analog MSB
  paket[2] = low_byte;      // Analog LSB
  paket[3] = button_state;  // Buton Durumu (0 veya 1)
  paket[4] = 0x55;          // Bitiş damgası (Tail)

  Serial.write(paket, 5);

  delay(50); // Saniyede 20 paket
}
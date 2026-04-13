#define FLASH_LED 4

void setup() {
  // put your setup code here, to run once:
   pinMode(FLASH_LED, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(FLASH_LED, HIGH); // Turn the flash ON
  delay(1000);                   // Wait for 1 second
  digitalWrite(FLASH_LED, LOW);  // Turn the flash OFF
  delay(1000);                   // Wait for 1 second

}

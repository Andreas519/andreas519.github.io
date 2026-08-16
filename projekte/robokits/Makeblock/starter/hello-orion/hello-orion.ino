const unsigned long AUSGABE_INTERVALL_MS = 500;

unsigned long letzteAusgabe = 0;
bool ledAn = false;

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("Hallo Orion!");
}

void loop()
{
  const unsigned long jetzt = millis();

  if (jetzt - letzteAusgabe >= AUSGABE_INTERVALL_MS)
  {
    letzteAusgabe = jetzt;
    ledAn = !ledAn;
    digitalWrite(LED_BUILTIN, ledAn ? HIGH : LOW);
    Serial.println("Hallo Orion!");
  }
}
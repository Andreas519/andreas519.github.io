#include <Wire.h>
#include <MeOrion.h>

const char PROGRAMM_NAME[] = "orion-steuerung";
const char PROGRAMM_VERSION[] = "1.3.0";
const char PROTOKOLL_VERSION[] = "1";
const char MAKEBLOCKDRIVE_VERSION[] = "3.27";
const unsigned long TELEMETRIE_INTERVALL_MS = 250;
const unsigned long FAHRBEFEHL_TIMEOUT_MS = 1000;
const unsigned long BLINK_INTERVALL_GETRENNT_MS = 100;
const unsigned long BLINK_INTERVALL_VERBUNDEN_MS = 1000;
const uint8_t BEFEHL_PUFFER_GROESSE = 48;

// Nur Sensoren aktivieren, die wirklich am angegebenen Port angeschlossen sind.
// #define SENSOR_ULTRASCHALL
// #define SENSOR_LINIENFOLGER
// #define SENSOR_LICHT
// #define SENSOR_SCHALL
// #define SENSOR_BEWEGUNG
// #define SENSOR_TEMPERATUR
// #define SENSOR_GYRO
// #define SENSOR_KOMPASS

MeDCMotor motorLinks(M1);
MeDCMotor motorRechts(M2);
MePort servoPort(PORT_3);
Servo servoMotor;
const uint8_t SERVO_PIN = servoPort.pin1();

#ifdef SENSOR_ULTRASCHALL
MeUltrasonicSensor ultraschallSensor(PORT_3);
#endif
#ifdef SENSOR_LINIENFOLGER
MeLineFollower linienSensor(PORT_4);
#endif
#ifdef SENSOR_LICHT
MeLightSensor lichtSensor(PORT_6);
#endif
#ifdef SENSOR_SCHALL
MeSoundSensor schallSensor(PORT_7);
#endif
#ifdef SENSOR_BEWEGUNG
MePIRMotionSensor bewegungsSensor(PORT_4);
#endif
#ifdef SENSOR_TEMPERATUR
MeTemperature temperaturSensor(PORT_8, SLOT2);
#endif
#ifdef SENSOR_GYRO
MeGyro gyroSensor;
#endif
#ifdef SENSOR_KOMPASS
MeCompass kompassSensor(PORT_4);
#endif

char befehlPuffer[BEFEHL_PUFFER_GROESSE];
uint8_t befehlLaenge = 0;
unsigned long letzteTelemetrie = 0;
unsigned long letzterFahrbefehl = 0;
unsigned long letzterLedWechsel = 0;
bool fahrzeugAktiv = false;
bool steuerprogrammVerbunden = false;
bool statusLedAn = false;

int begrenzeMotorwert(long wert)
{
  return constrain(wert, -255, 255);
}

void halt()
{
  motorLinks.stop();
  motorRechts.stop();
  fahrzeugAktiv = false;
}

void fahre(int links, int rechts)
{
  motorLinks.run(links);
  motorRechts.run(-rechts);
  letzterFahrbefehl = millis();
  fahrzeugAktiv = links != 0 || rechts != 0;
}

bool liesMotorwert(char *text, int &wert)
{
  if (text == NULL || *text == '\0')
  {
    return false;
  }

  char *ende;
  const long eingabe = strtol(text, &ende, 10);
  if (*ende != '\0' || eingabe < -255 || eingabe > 255)
  {
    return false;
  }

  wert = begrenzeMotorwert(eingabe);
  return true;
}

bool liesServowinkel(char *text, int &winkel)
{
  if (text == NULL || *text == '\0')
  {
    return false;
  }

  char *ende;
  const long eingabe = strtol(text, &ende, 10);
  if (*ende != '\0' || eingabe < 0 || eingabe > 180)
  {
    return false;
  }

  winkel = eingabe;
  return true;
}

void bestaetigeFahrt(int links, int rechts)
{
  Serial.print(F("OK,f,"));
  Serial.print(links);
  Serial.print(',');
  Serial.println(rechts);
}

void sendeAktiveSensoren()
{
  Serial.print(F("ID,sensoren="));
#ifdef SENSOR_ULTRASCHALL
  Serial.print(F("ultraschall@PORT_3;"));
#endif
#ifdef SENSOR_LINIENFOLGER
  Serial.print(F("linienfolger@PORT_4;"));
#endif
#ifdef SENSOR_LICHT
  Serial.print(F("licht@PORT_6;"));
#endif
#ifdef SENSOR_SCHALL
  Serial.print(F("schall@PORT_7;"));
#endif
#ifdef SENSOR_BEWEGUNG
  Serial.print(F("bewegung@PORT_4;"));
#endif
#ifdef SENSOR_TEMPERATUR
  Serial.print(F("temperatur@PORT_8/SLOT2;"));
#endif
#ifdef SENSOR_GYRO
  Serial.print(F("gyro@I2C;"));
#endif
#ifdef SENSOR_KOMPASS
  Serial.print(F("kompass@I2C/PORT_4;"));
#endif
  Serial.println();
}

void sendePortbelegung()
{
  Serial.print(F("ID,ports=motor_links@M1;motor_rechts@M2;servo@PORT_3/SLOT1/D12;status_led@D13;usb_uart@D0_RX+D1_TX;"));
#ifdef SENSOR_ULTRASCHALL
  Serial.print(F("ultraschall@PORT_3;"));
#endif
#ifdef SENSOR_LINIENFOLGER
  Serial.print(F("linienfolger@PORT_4;"));
#endif
#ifdef SENSOR_LICHT
  Serial.print(F("licht@PORT_6;"));
#endif
#ifdef SENSOR_SCHALL
  Serial.print(F("schall@PORT_7;"));
#endif
#ifdef SENSOR_BEWEGUNG
  Serial.print(F("bewegung@PORT_4;"));
#endif
#ifdef SENSOR_TEMPERATUR
  Serial.print(F("temperatur@PORT_8/SLOT2;"));
#endif
#ifdef SENSOR_GYRO
  Serial.print(F("gyro@I2C;"));
#endif
#ifdef SENSOR_KOMPASS
  Serial.print(F("kompass@I2C/PORT_4;"));
#endif
  Serial.println();
}

void sendeIdentifikation()
{
  Serial.print(F("ID,programm="));
  Serial.print(PROGRAMM_NAME);
  Serial.print(F(",version="));
  Serial.print(PROGRAMM_VERSION);
  Serial.print(F(",protokoll="));
  Serial.println(PROTOKOLL_VERSION);

  Serial.print(F("ID,board=Me Orion,mcu=ATmega328P,profil=arduino:avr:uno,makeblockdrive="));
  Serial.println(MAKEBLOCKDRIVE_VERSION);

  Serial.print(F("ID,build="));
  Serial.print(F(__DATE__));
  Serial.print(' ');
  Serial.println(F(__TIME__));
  sendePortbelegung();
  sendeAktiveSensoren();
}

void verarbeiteBefehl(char *zeile)
{
  char *befehl = strtok(zeile, " ");
  if (befehl == NULL)
  {
    return;
  }

  if (strcmp(befehl, "i") == 0)
  {
    steuerprogrammVerbunden = true;
    sendeIdentifikation();
    return;
  }

  if (strcmp(befehl, "h") == 0 || strcmp(befehl, "0") == 0)
  {
    halt();
    Serial.println(F("OK,h"));
    return;
  }

  char *ersterParameter = strtok(NULL, " ");
  char *zweiterParameter = strtok(NULL, " ");
  char *weitererParameter = strtok(NULL, " ");
  int ersterWert;
  int zweiterWert;

  if (strcmp(befehl, "s") == 0)
  {
    if (!liesServowinkel(ersterParameter, ersterWert) || zweiterParameter != NULL)
    {
      Serial.println(F("ERR,s erwartet: s <winkel 0..180>"));
      return;
    }

    servoMotor.write(ersterWert);
    if (!servoMotor.attached())
    {
      servoMotor.attach(SERVO_PIN);
    }
    Serial.print(F("OK,s,"));
    Serial.println(ersterWert);
    return;
  }

  if (strcmp(befehl, "f") == 0)
  {
    if (!liesMotorwert(ersterParameter, ersterWert) || weitererParameter != NULL)
    {
      Serial.println(F("ERR,f erwartet: f <wert> [rechts]"));
      return;
    }

    if (zweiterParameter == NULL)
    {
      zweiterWert = ersterWert;
    }
    else if (!liesMotorwert(zweiterParameter, zweiterWert))
    {
      Serial.println(F("ERR,f erwartet Motorwerte -255..255"));
      return;
    }

    fahre(ersterWert, zweiterWert);
    bestaetigeFahrt(ersterWert, zweiterWert);
    return;
  }

  if ((strcmp(befehl, "l") == 0 || strcmp(befehl, "r") == 0) &&
      liesMotorwert(ersterParameter, ersterWert) && zweiterParameter == NULL)
  {
    const int links = strcmp(befehl, "l") == 0 ? ersterWert : 0;
    const int rechts = strcmp(befehl, "r") == 0 ? ersterWert : 0;
    fahre(links, rechts);
    bestaetigeFahrt(links, rechts);
    return;
  }

  Serial.println(F("ERR,Befehle: i | h | f <wert> [rechts] | l <wert> | r <wert> | s <winkel>"));
}

void empfangeBefehle()
{
  while (Serial.available() > 0)
  {
    const char zeichen = Serial.read();

    if (zeichen == '\n' || zeichen == '\r')
    {
      if (befehlLaenge > 0)
      {
        befehlPuffer[befehlLaenge] = '\0';
        verarbeiteBefehl(befehlPuffer);
        befehlLaenge = 0;
      }
    }
    else if (befehlLaenge < BEFEHL_PUFFER_GROESSE - 1)
    {
      befehlPuffer[befehlLaenge++] = zeichen;
    }
    else
    {
      befehlLaenge = 0;
      Serial.println(F("ERR,Befehl zu lang"));
    }
  }
}

void sendeTelemetrie()
{
  Serial.print(F("TEL,"));
  Serial.print(millis());

#ifdef SENSOR_ULTRASCHALL
  Serial.print(F(",abstand_cm="));
  Serial.print(ultraschallSensor.distanceCm(), 1);
#endif
#ifdef SENSOR_LINIENFOLGER
  Serial.print(F(",linie="));
  Serial.print(linienSensor.readSensors());
#endif
#ifdef SENSOR_LICHT
  Serial.print(F(",licht="));
  Serial.print(lichtSensor.read());
#endif
#ifdef SENSOR_SCHALL
  Serial.print(F(",schall="));
  Serial.print(schallSensor.strength());
#endif
#ifdef SENSOR_BEWEGUNG
  Serial.print(F(",bewegung="));
  Serial.print(bewegungsSensor.isHumanDetected() ? 1 : 0);
#endif
#ifdef SENSOR_TEMPERATUR
  Serial.print(F(",temperatur_c="));
  Serial.print(temperaturSensor.temperature(), 1);
#endif
#ifdef SENSOR_GYRO
  Serial.print(F(",gyro_x_deg="));
  Serial.print(gyroSensor.getAngleX(), 1);
  Serial.print(F(",gyro_y_deg="));
  Serial.print(gyroSensor.getAngleY(), 1);
  Serial.print(F(",gyro_z_deg="));
  Serial.print(gyroSensor.getAngleZ(), 1);
#endif
#ifdef SENSOR_KOMPASS
  int16_t kompassX;
  int16_t kompassY;
  int16_t kompassZ;
  const int16_t kompassStatus = kompassSensor.getHeading(&kompassX, &kompassY, &kompassZ);
  Serial.print(F(",kompass_status="));
  Serial.print(kompassStatus);
  if (kompassStatus == 0)
  {
    Serial.print(F(",kompass_deg="));
    Serial.print(kompassSensor.getAngle(), 1);
    Serial.print(F(",kompass_x="));
    Serial.print(kompassX);
    Serial.print(F(",kompass_y="));
    Serial.print(kompassY);
    Serial.print(F(",kompass_z="));
    Serial.print(kompassZ);
  }
#endif

  Serial.println();
}

void setup()
{
  halt();
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
#ifdef SENSOR_GYRO
  gyroSensor.begin();
#endif
#ifdef SENSOR_KOMPASS
  kompassSensor.begin();
  Serial.println(kompassSensor.testConnection() ? F("INFO,Kompass bereit") : F("ERR,Kompass nicht gefunden"));
#endif
  Serial.print(F("READY,"));
  Serial.print(PROGRAMM_NAME);
  Serial.print(',');
  Serial.println(PROGRAMM_VERSION);
  Serial.println(F("INFO,Befehle: i | h | f <wert> [rechts] | l <wert> | r <wert> | s <winkel>"));
}

void loop()
{
  empfangeBefehle();
#ifdef SENSOR_GYRO
  gyroSensor.update();
#endif

  const unsigned long jetzt = millis();
  const unsigned long blinkIntervall = steuerprogrammVerbunden
                                           ? BLINK_INTERVALL_VERBUNDEN_MS
                                           : BLINK_INTERVALL_GETRENNT_MS;
  if (jetzt - letzterLedWechsel >= blinkIntervall)
  {
    letzterLedWechsel = jetzt;
    statusLedAn = !statusLedAn;
    digitalWrite(LED_BUILTIN, statusLedAn ? HIGH : LOW);
  }

  if (fahrzeugAktiv && jetzt - letzterFahrbefehl >= FAHRBEFEHL_TIMEOUT_MS)
  {
    halt();
    Serial.println(F("SAFE,timeout"));
  }

  if (jetzt - letzteTelemetrie >= TELEMETRIE_INTERVALL_MS)
  {
    letzteTelemetrie = jetzt;
    sendeTelemetrie();
  }
}
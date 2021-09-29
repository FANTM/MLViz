/* Set these parameters based on your hardware setup */
#define BAUD 2000000
#define NUM_DEVLPRS 2
int DEVLPR_PINS[] = {A0,A1};
int EMG_VALS[NUM_DEVLPRS];
/*****************************************************/

byte bufOut[4];
volatile bool dataReady = false;

ISR(TIMER0_COMPA_vect) {  // Timer0 interrupt, 1kHz
    if (!dataReady) {
        for (int i = 0; i < NUM_DEVLPRS; i++) {
            EMG_VALS[i] = analogRead(DEVLPR_PINS[i]);
        }
        dataReady = true;
    }
}

void setup() {
    cli();  // Stop interrupts
    //set timer0 interrupt at 1kHz
    TCCR0A = 0;// set entire TCCR0A register to 0
    TCCR0B = 0;// same for TCCR0B
    TCNT0  = 0;//initialize counter value to 0
    // set compare match register for 1khz increments
    OCR0A = 249;// = (16*10^6) / (1000*64) - 1 (must be <256)
    // turn on CTC mode
    TCCR0A |= (1 << WGM01);
    // Set CS01 and CS00 bits for 64 prescaler
    TCCR0B |= (1 << CS01) | (1 << CS00);
    // enable timer compare interrupt
    TIMSK0 |= (1 << OCIE0A);
    sei();  // Start interrupts

    Serial.begin(BAUD);
}

/* Safety check in case the alias of A0-A5 isn't directly mapped to the number
 we expect */
byte normalizePin(int analogPin) {
    switch (analogPin)
    {
    case A0:
        return 0;
    case A1:
        return 1;
    case A2:
        return 2;
    case A3:
        return 3;
    case A4:
        return 4;
    case A5:
        return 5;
    default:
        return 0xff;
    }
}

/* Helper function for formatting data in the way that the daemon expects */
void fillPacket(byte *buffOut, byte pin, int value) {
    // pack 16-bits for the emg value and 4 bits for the pin into
    // three bytes in the following fashion (e=emg, p=pin)
    // eeee eee0
    // eeee eee0
    // eepp pp00
    // and terminate with a 1
    // 0000 0001
    buffOut[0] = (value >> 8) & 0xFE;
    buffOut[1] = (value >> 1) & 0xFE;
    buffOut[2] = ((value << 6) & 0xC0) | ((pin << 2) & 0x3C);
    buffOut[3] = 0x01;
}

void loop() {
    if (dataReady) {
        for (int i = 0; i < NUM_DEVLPRS; i++) {
            fillPacket(bufOut, normalizePin(DEVLPR_PINS[i]), EMG_VALS[i]);
            Serial.write(bufOut, 4);
        }
        dataReady = false;
    }
}

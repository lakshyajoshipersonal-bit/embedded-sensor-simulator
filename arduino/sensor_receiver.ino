float temperature = 0;
int lightLevel = 1000;
int LED_pin = 6;
enum state {NORMAL, OVERHEAT, DARK, OVERHEAT_DARK, FAULT};
enum FaultCode {NO_FAULT,INVALID_TEMP,TEMP_RANGE,INVALID_LIGHT,LIGHT_RANGE};
state systemState = NORMAL;
FaultCode fault = NO_FAULT;


void setup() {
    Serial.begin(9600);
    pinMode(LED_pin, OUTPUT);
}

bool isValidNumber(String value){
    if (value.length() == 0){
        return false;
    }

    bool decimalSeen = false;
    for(int i = 0; i<value.length(); i++){
        char c = value[i];
        if (c == '-' && i == 0){
            continue;
        }
        if (c == '.' && !decimalSeen){
            decimalSeen = true;
            continue;
        }

        if(!isDigit(c)){
            return false;
        }
    }
    return true;
}

void loop() {

    if (Serial.available() > 0) {

        String data = Serial.readStringUntil('\n');

        // Temperature message
        if (data.startsWith("TEMP:")) {

            String value = data.substring(5);

            if(!isValidNumber(value)){
                systemState = FAULT;
                fault = INVALID_TEMP;
                digitalWrite(LED_pin, LOW);
                sendFault();
                return;
            }

            float new_temperature = value.toFloat();

            if(new_temperature < -40 || new_temperature > 125){
                systemState = FAULT;
                fault = TEMP_RANGE;
                digitalWrite(LED_pin, LOW);
                sendFault();
                return;
            }

            temperature = new_temperature;

        }

        // Light message
        else if (data.startsWith("LIGHT:")) {

            String value = data.substring(6);

            if(!isValidNumber(value)){
                systemState = FAULT;
                fault = INVALID_LIGHT;
                digitalWrite(LED_pin, LOW);
                sendFault();
                return;
            }

            int new_lightLevel = value.toInt();

            if (new_lightLevel < 0 || new_lightLevel > 1000){
                systemState = FAULT;
                fault = LIGHT_RANGE;
                digitalWrite(LED_pin, LOW);
                sendFault();
                return;
            }
            lightLevel = new_lightLevel;

        }    

        else if(data.startsWith("QUIT")){
            digitalWrite(LED_pin, LOW);
            Serial.println("Quitting sensor");
            return;
            
        }

        else if(data.startsWith("RESET")){
            temperature = 22.0;
            lightLevel = 700;

            fault = NO_FAULT;
            systemState = NORMAL;
            digitalWrite(LED_pin, LOW);

            Serial.println("System Reset");
            return;
            

        }

        else {
            Serial.println("Unknown sensor type");
            return;
        }

        updateSystem();
    }
}


void updateSystem() {
    
    //Once a fault detected,we want it remembered, unless reset.
    if (systemState == FAULT){
        digitalWrite(LED_pin, LOW);
        sendsystemState();
        return;
    }

    // Temperature warning has priority
    if (temperature > 30 && lightLevel < 300) {
        systemState = OVERHEAT_DARK;
        digitalWrite(LED_pin, HIGH);
    }

    // Otherwise use automatic lighting
    else if (temperature > 30){
        systemState = OVERHEAT;
        digitalWrite(LED_pin, HIGH);
    }
    else if (lightLevel < 300) {
        systemState = DARK;
        digitalWrite(LED_pin, HIGH);
    }

    else {
        systemState = NORMAL;
        digitalWrite(LED_pin, LOW);
    }
    sendsystemState();
}

void sendsystemState(){
    Serial.print("STATE: ");

    switch(systemState){

        case NORMAL:
            Serial.println("NORMAL");
            break;
        case OVERHEAT:
            Serial.println("OVERHEAT");
            break;
        case DARK:
            Serial.println("DARK");
            break;
        case OVERHEAT_DARK:
            Serial.println("OVERHEAT_DARK");
            break;
        case FAULT:
            Serial.println("FAULT");
            break;
    }
}

void sendFault(){
    Serial.print("FAULT: ");

    switch(fault){
        case INVALID_TEMP:
            Serial.println("INVALID_TEMP");
            break;

        case TEMP_RANGE:
            Serial.println("TEMP_RANGE");
            break;

        case INVALID_LIGHT:
            Serial.println("INVALID_LIGHT");
            break;

        case LIGHT_RANGE:
            Serial.println("LIGHT_RANGE");
            break;

        default:
            Serial.println("UNKNOWN");
            break;
    }
}
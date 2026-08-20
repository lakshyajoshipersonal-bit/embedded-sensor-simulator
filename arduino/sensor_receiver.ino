float temperature = 0;
int lightLevel = 1000;
float humidity = 50.0;
int LED_pin = 6;
enum state {NORMAL, OVERHEAT, DARK, OVERHEAT_DARK, FAULT};
enum FaultCode {NO_FAULT,INVALID_TEMP,TEMP_RANGE,INVALID_LIGHT,LIGHT_RANGE,INVALID_HUMIDITY,HUMIDITY_RANGE};
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

void updateSystem() {
    
    systemState = determineSystemState();
    //Once a fault detected,we want it remembered, unless reset.
    if (systemState == FAULT){
        digitalWrite(LED_pin, LOW);
    }

    
    if (systemState == OVERHEAT || 
    systemState == DARK ||
    systemState == OVERHEAT_DARK){
        digitalWrite(LED_pin, HIGH);
    }

    else{
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
        
        case INVALID_HUMIDITY:
            Serial.println("INVALID_HUMIDITY");
            break;

        case HUMIDITY_RANGE:
            Serial.println("HUMIDITY_RANGE");
            break;
        
        

        default:
            Serial.println("UNKNOWN");
            break;
    }
}

state determineSystemState(){
    if (systemState == FAULT){
        return FAULT;
    }
    if (temperature > 30 && lightLevel < 300){
        return OVERHEAT_DARK;
    }
    if (temperature > 30){
        return OVERHEAT;
    }
    if (lightLevel < 300){
        return DARK;
    }
    return NORMAL;
}

bool handleTemperature(String data){
    String value = data.substring(5);

    if(!isValidNumber(value)){
        systemState = FAULT;
        fault = INVALID_TEMP;
        digitalWrite(LED_pin, LOW);
        sendFault();
        return false;
        }

    float new_temperature = value.toFloat();

    if(new_temperature < -40 || new_temperature > 125){
        systemState = FAULT;
        fault = TEMP_RANGE;
        digitalWrite(LED_pin, LOW);
        sendFault();
        return false;
    }

    temperature = new_temperature;
    return true;
}

bool handleLight(String data){
    String value = data.substring(6);
    if(!isValidNumber(value)){
        systemState = FAULT;
        fault = INVALID_LIGHT;
        digitalWrite(LED_pin, LOW);
        sendFault();
        return false;
    }

    int new_lightLevel = value.toInt();

    if (new_lightLevel < 0 || new_lightLevel > 1000){
        systemState = FAULT;
        fault = LIGHT_RANGE;
        digitalWrite(LED_pin, LOW);
        sendFault();
        return false;
    }
    lightLevel = new_lightLevel;
    return true;
}

bool handleHumidity(String data){
    String value = data.substring(9);

    if(!isValidNumber(value)){
        systemState = FAULT;
        fault = INVALID_HUMIDITY;
        digitalWrite(LED_pin, LOW);
        sendFault();
        return;
    }
    float new_humidity = value.toFloat();

    if(new_humidity < 0 || new_humidity > 100){
        systemState = FAULT;
        fault = HUMIDITY_RANGE;
        digitalWrite(LED_pin, LOW);
        sendFault();
        return;
    }
    humidity = new_humidity;
    return true;
}

void handleReset(){
    temperature = 22.0;
    lightLevel = 700;
    
    fault = NO_FAULT;
    systemState = NORMAL;
    digitalWrite(LED_pin, LOW);

    Serial.println("System Reset");
}

void handleQuit(){
    digitalWrite(LED_pin, LOW);
    Serial.println("Quitting sensor");
}

void handleCommand(String data){
    if (data.startsWith("TEMP:")){
        if(!handleTemperature(data)){
            return;
        }
    }

    // Light message
    else if (data.startsWith("LIGHT:")) {
        if(!handleLight(data)){
            return;
        }
    }

    //Humidity message
    else if (data.startsWith("HUMIDITY:")){
        if(!handleHumidity(data)){
            return;
        }
    }    

    else if(data.startsWith("QUIT")){
        handleQuit();
        return;
            
    }

    else if(data.startsWith("RESET")){
        handleReset();
        return;
    }

    else {
        Serial.println("Unknown sensor type");
        return;
    }

    updateSystem();
}

void loop(){

    if (Serial.available() > 0){

        String data = Serial.readStringUntil('\n');
        handleCommand(data);
    }
}
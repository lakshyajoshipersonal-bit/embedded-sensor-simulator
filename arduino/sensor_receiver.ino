float temperature = 22.0;
int lightLevel = 700;
float humidity = 50.0;
int LED_pin = 6;
float temp_threshold = 30.0;
int light_threshold = 300;
enum state {NORMAL, OVERHEAT, DARK, OVERHEAT_DARK, FAULT};
enum FaultCode {NO_FAULT,INVALID_TEMP,TEMP_RANGE,INVALID_LIGHT,LIGHT_RANGE,INVALID_HUMIDITY,HUMIDITY_RANGE};
state systemState = NORMAL;
FaultCode fault = NO_FAULT;

void setup() {
    Serial.begin(9600);
    pinMode(LED_pin, OUTPUT);
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

state determineSystemState(){
    if (systemState == FAULT){
        return FAULT;
    }
    if (temperature > temp_threshold && lightLevel < light_threshold){
        return OVERHEAT_DARK;
    }
    if (temperature > temp_threshold){
        return OVERHEAT;
    }
    if (lightLevel < light_threshold){
        return DARK;
    }
    return NORMAL;
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

void setFault(FaultCode newFault){
    systemState = FAULT;
    fault = newFault;

    digitalWrite(LED_pin, LOW);

    sendFault();
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

bool isValidNumber(String value){
    if (value.length() == 0){
        return false;
    }

    bool decimalSeen = false;
    bool digitSeen = false;
    for(int i = 0; i<value.length(); i++){
        char c = value[i];
        if (c == '-' && i == 0){
            continue;
        }
        if (c == '.' && !decimalSeen){
            decimalSeen = true;
            continue;
        }

        if(isDigit(c)){
            digitSeen = true;
            continue;
        }
        return false;
    }
    return digitSeen;
}
bool validateTemperature(String value, float& result){
    if(!isValidNumber(value)){
        setFault(INVALID_TEMP);
        return false;
    }
    result = value.toFloat();
    if(result < -40 || result > 125){
        setFault(TEMP_RANGE);
        return false;
    }
    return true;
}

bool validateLight(String value, int& result){
    if(!isValidNumber(value)){
        setFault(INVALID_LIGHT);
        return false;
    }
    result = value.toInt();
    if(result < 0|| result > 1000){
        setFault(LIGHT_RANGE);
        return false;
    }
    return true;
}

bool validateHumidity(String value, float& result){
    if(!isValidNumber(value)){
        setFault(INVALID_HUMIDITY);
        return false;
    }
    result = value.toFloat();
    if(result < 0|| result > 100){
        setFault(HUMIDITY_RANGE);
        return false;
    }
    return true;
}

bool handleSensors(String data) {

    String values = data.substring(8);

    int firstComma = values.indexOf(',');
    int secondComma = values.indexOf(',', firstComma + 1);

    if (firstComma == -1 || secondComma == -1) {
        Serial.println("INVALID_SENSORS_FORMAT");
        return false;
    }

    // Make sure there isn't an unexpected fourth value
    int thirdComma = values.indexOf(',', secondComma + 1);

    if (thirdComma != -1) {
        Serial.println("INVALID_SENSORS_FORMAT");
        return false;
    }

    String tempValue = values.substring(0, firstComma);

    String lightValue = values.substring(firstComma + 1, secondComma);

    String humidityValue = values.substring(secondComma + 1);

    float newTemperature;
    int newLightLevel;
    float newHumidity;

    // Validate EVERYTHING before changing actual sensor values

    if (!validateTemperature(tempValue, newTemperature)) {
        return false;
    }

    if (!validateLight(lightValue, newLightLevel)) {
        return false;
    }

    if (!validateHumidity(humidityValue, newHumidity)) {
        return false;
    }

    temperature = newTemperature;
    lightLevel = newLightLevel;
    humidity = newHumidity;

    return true;
}

void handleReset(){
    temperature = 22.0;
    lightLevel = 700;
    humidity = 50.0;
    fault = NO_FAULT;
    systemState = NORMAL;
    digitalWrite(LED_pin, LOW);

    Serial.println("System Reset");
}

void handleQuit(){
    digitalWrite(LED_pin, LOW);
    Serial.println("Quitting sensor");
}

void handleTempThreshold(String data) {

    String value = data.substring(15);

    if (!isValidNumber(value)) {
        Serial.println("INVALID_TEMP_THRESHOLD");
        return;
    }

    float newThreshold = value.toFloat();

    // Keeps threshold useful for simulator scenarios
    if (newThreshold < 15 || newThreshold >= 45) {
        Serial.println("TEMP_THRESHOLD_RANGE");
        return;
    }

    temp_threshold = newThreshold;

    Serial.print("TEMP_THRESHOLD: ");
    Serial.println(temp_threshold);
}


void handleLightThreshold(String data) {

    String value = data.substring(16);

    if (!isValidNumber(value)) {
        Serial.println("INVALID_LIGHT_THRESHOLD");
        return;
    }

    int newThreshold = value.toInt();

    // Keeps threshold useful for simulator scenarios
    if (newThreshold <= 0 || newThreshold > 1000) {
        Serial.println("LIGHT_THRESHOLD_RANGE");
        return;
    }

    light_threshold = newThreshold;

    Serial.print("LIGHT_THRESHOLD: ");
    Serial.println(light_threshold);
}

void handleCommand(String data){
    if (data.startsWith("SENSORS:")){
        if(!handleSensors(data)){
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

    else if(data.startsWith("TEMP_THRESHOLD:")){
        handleTempThreshold(data);
        return;
        
    }

    else if(data.startsWith("LIGHT_THRESHOLD:")){
        handleLightThreshold(data);
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
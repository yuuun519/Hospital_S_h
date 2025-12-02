#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>
#include <LiquidCrystal_I2C.h>

LCD 초기화
LiquidCrystal_I2C lcd(0x3F, 16, 2);

#define PN532_IRQ   (3)
#define PN532_RESET (2)

Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

전역 변수로 마지막으로 읽은 cardID 저장
String lastCardID = "";
unsigned long lastReadTime = 0;
bool cardPresent = false;

void setup(void) {
    Serial.begin(115200);  // 시리얼 통신 시작
    //lcd.init();           // LCD 초기화
    //lcd.backlight();
    //lcd.print("NFC READ READY");

    nfc.begin();           // PN532 초기화
}

void loop(void) {
    unsigned long currentMillis = millis();
    
    // NFC 카드가 있는지 감지
    if (!nfc.inListPassiveTarget()) {
        if (cardPresent) {
            // 카드가 감지되지 않으면, 마지막 카드가 제거된 것으로 간주
            //lcd.clear();
            //lcd.print("Please Next CARD");
            cardPresent = false; // 상태를 업데이트
            lastCardID = "";     // 마지막 카드ID를 초기화하여 재인식이 가능하게 함
        }
        return;
    }

    // 카드 UID 읽기
    uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
    uint8_t uidLength;

    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength)) {
        // 카드 UID를 String으로 변환
        String cardID = "";
        for (uint8_t i = 0; i < uidLength; i++) {
            cardID += String(uid[i], HEX);
            if (i < uidLength - 1) {
                cardID += ":"; // 각 바이트를 ':'로 구분
            }
        }

        if (cardID != lastCardID) {
            // 새로운 카드가 감지된 경우
            lastReadTime = currentMillis; // 마지막 읽기 시간 업데이트
            lastCardID = cardID; // 마지막 카드 ID 업데이트
            cardPresent = true; // 카드가 인식된 상태 유지
            
           lcd.clear();
           lcd.setCursor(0, 0);
           lcd.print("READ CARD:");
           lcd.setCursor(0, 1);
           lcd.print(cardID);
            
            // 카드 상태를 시리얼로 출력
            Serial.println(cardID);
        } else {
            // 동일 카드를 인식 중일 때
            if (currentMillis - lastReadTime < 10000) {
                // 10초 이내에 다시 인식
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("READING...");
              lcd.setCursor(0, 1);
              lcd.print(cardID);
            }
        }

        delay(1000); // 1초 대기 후 다음 인식 대기
    } 
}

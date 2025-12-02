#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

#define PN532_IRQ   (3)
#define PN532_RESET (2)

Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

String lastCardID = "";
unsigned long lastReadTime = 0;
bool cardPresent = false;

void setup(void) {
    Serial.begin(115200);  
    
    Serial.println("--------------------------------");
    Serial.println("Arduino NFC System Start");
    Serial.println("Connecting to PN532...");

    nfc.begin();           // PN532 초기화
    
    // 펌웨어 버전 확인 (연결 확인용)
    uint32_t versiondata = nfc.getFirmwareVersion();
    if (! versiondata) {
        // 연결 실패 시 메시지 출력 후 무한 루프
        Serial.println("!! 오류: PN532 보드를 찾을 수 없습니다 !!");
        Serial.println("1. 배선을 확인하세요 (SDA->A4, SCL->A5)");
        Serial.println("2. PN532 보드의 딥스위치가 I2C 모드인지 확인하세요");
        while (1); 
    }
    
    // 연결 성공 시
    Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX); 
    Serial.println("Firmware ver. " + String((versiondata>>16) & 0xFF, DEC) + "." + String((versiondata>>8) & 0xFF, DEC));
    
    // 보드 설정 (SAMConfig는 읽기 안정성을 높여줍니다)
    nfc.SAMConfig();
    Serial.println("NFC Reader Ready! (Waiting for card...)");
    Serial.println("--------------------------------");
}

void loop(void) {
    unsigned long currentMillis = millis();
    
    // NFC 카드가 있는지 감지 (ISO14443A - 일반적인 카드)
    uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
    uint8_t uidLength;

    // 카드를 읽었는지 확인
    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength)) {
        
        String cardID = "";
        for (uint8_t i = 0; i < uidLength; i++) {
            if (uid[i] < 0x10) {
                cardID += "0";
            }
            cardID += String(uid[i], HEX);
            if (i < uidLength - 1) {
                cardID += ":"; 
            }
        }

        // 중복 인식 방지 로직
        if (cardID != lastCardID) {
            lastReadTime = currentMillis; 
            lastCardID = cardID; 
            cardPresent = true; 
            
            Serial.print("4:");
            Serial.println(cardID); 
            
        } else {
            // 동일 카드가 계속 올려져 있는 경우
            lastReadTime = currentMillis; 
        }
        
    } else {
        // 카드가 감지되지 않음
        if (cardPresent) {
             if (currentMillis - lastReadTime > 100) { 
                cardPresent = false;
                lastCardID = ""; 
                // Serial.println("Card Removed"); // 디버깅 필요시 주석 해제
             }
        }
    }
}
"""
수정일 : 2025-12-02
버전 : 3.0.0
"""

# ---------------------------------------------------------
# 00. 라이브러리 및 설정
# ---------------------------------------------------------
import sys
import serial
import serial.tools.list_ports 
import sqlite3
import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QStackedWidget,
    QRadioButton, QSizePolicy, QMessageBox, QSpacerItem, 
    QGraphicsDropShadowEffect, QDialog, QComboBox, QGroupBox 
)
from PyQt5.QtCore import (
    Qt, QSize, QTimer, pyqtSignal, QObject, QPropertyAnimation, 
    QSequentialAnimationGroup, QEasingCurve, QPoint, QRect
)
from PyQt5.QtGui import QFont, QColor, QFontDatabase

# ---------------------------------------------------------
# 01. DB 설정 및 초기화
# ---------------------------------------------------------

# 환자 데이터베이스
DB_FILE = "patient_db.sqlite3"

def connect_to_database():
    conn = sqlite3.connect(DB_FILE)
    return conn

def initialize_patient_db():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients_l (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cardnumber TEXT,
            registrationnumber TEXT UNIQUE,
            name TEXT,
            residentnumber TEXT,
            fbirth TEXT,
            age INTEGER,
            gender TEXT,
            phonenumber TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# 직원 데이터베이스
EMPLOYEE_DB_FILE = "employee_db.sqlite3"
logged_in_user_name = "Guest" 
age_numeric = None # 전역 변수 초기화

def connect_to_employee_db():
    conn = sqlite3.connect(EMPLOYEE_DB_FILE)
    return conn

def initialize_employee_db():
    conn = connect_to_employee_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# DB 초기화 실행
initialize_patient_db()
initialize_employee_db()

# ---------------------------------------------------------
# 02. 스타일
# ---------------------------------------------------------
QSS_STYLE = """
/* 기본 */
QWidget {
    font-family: 'Hakgyoansim Boadmarker R', 'Malgun Gothic';
    font-size: 16pt;
    color: #5D5D5D; 
    background-color: #FFF9F0;
}

/* 카드형 Frame*/
QFrame {
    background-color: transparent; 
    border-radius: 20px;
    border: none; 
}
QFrame#SystemCardFrame {
    background-color: #FFFFFF;
    border-radius: 20px;
}

/* 입력 필드 */
QLineEdit {
    background-color: #E8E4DF; 
    border: none;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 12pt;
    color: #5D5D5D;
    height: 30px;
}
QLineEdit:focus {
    background-color: #F0EBE6;
}
QLineEdit#NoBorder {
    background-color: #D8CFC9; 
    border: none;
    border-radius: 5px; 
    padding: 5px;
}

/* 콤보박스 (시스템 설정) */
QComboBox {
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 14px;
    background-color: #FAFAFA;
    color: #333333;
}
QComboBox::drop-down {
    border: none;
}

/* 버튼 스타일 */
QPushButton {
    border-radius: 5px;
    padding: 5px 15px;
    font-size: 12pt;
    font-weight: bold;
    color: #FFFFFF;
    border: none;
}
QPushButton#PrimaryButton { background-color: #DFA894; height: 30px; }
QPushButton#PrimaryButton:hover { background-color: #D49A85; }

QPushButton#SecondaryButton { background-color: #DFA894; }
QPushButton#SecondaryButton:hover { background-color: #D49A85; }

QPushButton#TertiaryButton { background-color: #C0C0C0; color: #333333; }
QPushButton#TertiaryButton:hover { background-color: #B0B0B0; }

QPushButton#SearchButton { background-color: #C5DCA0; color: #5D5D5D; }
QPushButton#SearchButton:hover { background-color: #B5CC90; }

QPushButton#MenuButton {
    background-color: #F8F5F2; color: #5D5D5D; border-radius: 20px;
    border: none; min-height: 120px; min-width: 120px; padding: 15px; font-size: 14pt;
}
QPushButton#MenuButton:hover { background-color: #EFEBE7; }
QPushButton#MenuButton[enabled="false"] { background-color: #F4EBE4; color: transparent; }

QPushButton#SignupButton {
    background-color: transparent; color: #888888; font-size: 12pt;
    font-weight: normal; border: none; padding: 5px;
}
QPushButton#SignupButton:hover { color: #DFA894; text-decoration: underline; }

QPushButton#LogoutButton {
    background-color: #DFA894; color: #FFFFFF; font-size: 12pt;
    font-weight: bold; border-radius: 5px; padding: 5px 10px; min-width: 80px; height: 30px;
}

/* 시스템 설정 전용 버튼 */
QPushButton#RefreshButton {
    background-color: #F0F0F0; border: 1px solid #CCCCCC;
    border-radius: 5px; color: #333333; font-size: 13px; font-weight: normal;
}
QPushButton#RefreshButton:hover { background-color: #E0E0E0; }

QPushButton#ConnectButton {
    background-color: #DFA894; color: white; border-radius: 8px;
    font-size: 16px; font-weight: bold; border: none;
}
QPushButton#ConnectButton:hover { background-color: #DFA894; }
QPushButton#ConnectButton:disabled { background-color: #A0A0A0; }

QPushButton#CloseButton {
    background-color: transparent; color: #A0A0A0; border: none;
    font-size: 18pt; padding: 0px; font-family: 'Malgun Gothic';
}
QPushButton#CloseButton:hover { color: #E88D83; }

/* 라디오 버튼 */
QRadioButton { spacing: 10px; font-size: 13pt; color: #5D5D5D; background-color: #FFFFFF; }
QRadioButton::indicator { width: 15px; height: 15px; }
QRadioButton::indicator::unchecked { border: 2px solid #DEDBD6; border-radius: 9px; background-color: #FFFFFF; }
QRadioButton::indicator::checked { border: 2px solid #DEDBD6; border-radius: 9px; background-color: #DFA894; }
"""

# ---------------------------------------------------------
# 03.메시지 박스 커스텀
# ---------------------------------------------------------
class CustomMessageBox(QDialog):
    def __init__(self, title, message, icon_type="Info", parent=None, buttons="Ok"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 200)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; border-radius: 15px; border: 1px solid #EAEAEA; }
            QLabel { font-size: 12pt; color: #5D5D5D; background-color: transparent; border: none; }
            QPushButton {
                background-color: #DFA894; color: white; border-radius: 8px;
                padding: 8px 20px; font-weight: bold; font-size: 11pt;
            }
            QPushButton:hover { background-color: #D49A85; }
            QPushButton#CancelButton { background-color: #C0C0C0; color: #333333; }
            QPushButton#CancelButton:hover { background-color: #B0B0B0; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        if buttons == "YesNo":
            yes_btn = QPushButton("예")
            yes_btn.clicked.connect(self.accept) 
            no_btn = QPushButton("아니오")
            no_btn.setObjectName("CancelButton")
            no_btn.clicked.connect(self.reject) 
            btn_layout.addWidget(yes_btn)
            btn_layout.addSpacing(10)
            btn_layout.addWidget(no_btn)
        else:
            ok_btn = QPushButton("확인")
            ok_btn.clicked.connect(self.accept)
            btn_layout.addWidget(ok_btn)
            
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

    @staticmethod
    def show_message(parent, title, message, icon_type="Info"):
        dlg = CustomMessageBox(title, message, icon_type, parent, buttons="Ok")
        dlg.exec_()

    @staticmethod
    def ask_yes_no(parent, title, message):
        dlg = CustomMessageBox(title, message, "Question", parent, buttons="YesNo")
        return dlg.exec_() == QDialog.Accepted


# ---------------------------------------------------------
# 04. 시리얼 리스너
# ---------------------------------------------------------
class SerialListener(QObject):
    card_detected_signal = pyqtSignal(str)
    
    def __init__(self, port, baudrate):
        super().__init__()
        self.arduino = None
        self.last_cardnumber = ''
        self.card_processing = False
        self.baudrate = baudrate 
        
        # [중요] 변수 초기화 위치 보장
        self.connection_error_printed = False 
        
        try:
            self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=.1)
            print(f"[시스템] 시리얼 포트 연결 성공: {port} (속도: {baudrate})")
            print(f"➜ 아두이노 코드의 Serial.begin({baudrate}); 와 일치하는지 확인하세요.")
        except Exception as e:
            print(f"[시스템] 초기 연결 실패 ({port}): {e}")
            print("➜ [시스템 설정] 메뉴로 이동하여 올바른 포트를 선택하고 '연결' 버튼을 눌러주세요.")
            self.arduino = None

    def is_valid_cardnumber(self, data):
        # '4:'로 시작하고 길이가 10자 이상인지 확인
        return data.startswith("4:") and len(data) > 10

    def read_from_arduino(self):
        # 1. 연결 상태 확인
        if not self.arduino or not self.arduino.is_open:
            # [안전장치] getattr을 사용하여 변수가 없더라도 에러 없이 기본값(False) 사용
            if not getattr(self, 'connection_error_printed', False):
                print("[대기 중] 아두이노와 연결되어 있지 않습니다. 시스템 설정에서 연결해주세요.")
                self.connection_error_printed = True # 한 번만 출력하고 잠잠히 대기
            return

        # 연결에 성공했다면 에러 플래그 리셋 (나중에 끊기면 다시 출력하기 위함)
        self.connection_error_printed = False

        # 2. 데이터 수신 확인
        try:
            if self.arduino.in_waiting > 0:
                # 데이터 읽기 시도
                raw_data = self.arduino.readline()
                
                # [디버깅] Raw 데이터 출력 (깨진 문자라도 확인 가능하게 함)
                # print(f"[Raw Data] {raw_data}") 
                
                try:
                    data = raw_data.decode('utf-8').strip()
                except UnicodeDecodeError:
                    print(f"[오류] 데이터 깨짐 발생! Raw: {raw_data}")
                    print("➜ Baudrate(통신속도)가 115200으로 맞는지 확인하세요.")
                    return

                if data:
                    print(f"[아두이노 수신] '{data}'") # 수신된 모든 문자열 출력
                    
                    if not self.card_processing:
                        if self.is_valid_cardnumber(data):
                            if data != self.last_cardnumber:
                                self.last_cardnumber = data
                                self.card_processing = True
                                print(f"[시스템] ✅ 유효한 카드 감지됨! 신호 전송: {data}")
                                self.card_detected_signal.emit(data)
                            else:
                                print(f"[무시] 중복된 카드 태그입니다: {data}")
                        else:
                            # 유효하지 않은 데이터가 들어오면 이유를 출력
                            print(f"[무시] 형식에 맞지 않는 데이터: '{data}' (조건: '4:'로 시작)")
        
        except Exception as e:
            print(f"[오류] 시리얼 읽기 중 예외 발생: {e}")
            # 읽기 중 에러나면 연결이 끊긴 것으로 간주할 수도 있음
            # self.arduino.close() 
    
    def set_processing_done(self):
        self.card_processing = False
        self.last_cardnumber = ''

# ---------------------------------------------------------
# 05. 로그인 화면
# ---------------------------------------------------------
def authenticate_user(employee_id, password):
    conn = connect_to_employee_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password, name FROM employees WHERE employee_id = ?", (employee_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        stored_password, name = result
        if stored_password == password:
            return (True, "Success", name)
        else:
            return (False, "Verification needed", None)
    else:
        return (False, "Registration needed", None)

def register_user(name, employee_id, password):
    conn = connect_to_employee_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO employees (name, employee_id, password) VALUES (?, ?, ?)",
            (name, employee_id, password)
        )
        conn.commit()
        return True, "회원가입에 성공했습니다."
    except sqlite3.IntegrityError:
        return False, "이미 존재하는 사번입니다."
    except Exception as e:
        return False, f"데이터베이스 오류: {e}"
    finally:
        cursor.close()
        conn.close()


class LoginWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        card_frame = QFrame()
        card_frame.setFixedSize(450, 400)
        card_frame.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border-radius: 20px; }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))
        card_frame.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(50, 50, 50, 50)
        card_layout.setSpacing(15)

        title = QLabel("병원 행정 시스템")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Hakgyoansim Boadmarker R', 18, QFont.Bold))
        title.setStyleSheet("color: #E88D83; border: none; background-color: transparent;") 

        self.employee_id = QLineEdit()
        self.employee_id.setPlaceholderText("사번 ")
        self.password = QLineEdit()
        self.password.setPlaceholderText("비밀번호 ")
        self.password.setEchoMode(QLineEdit.Password)
        self.employee_id.returnPressed.connect(self.authenticate)
        self.password.returnPressed.connect(self.authenticate)

        login_btn = QPushButton("로그인")
        login_btn.setObjectName("PrimaryButton")
        login_btn.clicked.connect(self.authenticate)
        
        signup_btn = QPushButton("회원가입")
        signup_btn.setObjectName("SignupButton")
        signup_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        card_layout.addWidget(title)
        card_layout.addSpacing(30)
        card_layout.addWidget(self.employee_id)
        card_layout.addWidget(self.password)
        card_layout.addSpacing(20)
        card_layout.addWidget(login_btn)
        card_layout.addSpacing(12) 
        card_layout.addWidget(signup_btn, alignment=Qt.AlignCenter)
        card_layout.addStretch(1) 
        
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(card_frame)
        h_layout.addStretch(1)
        
        main_layout = QVBoxLayout(self)
        main_layout.addStretch(1)
        main_layout.addLayout(h_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def authenticate(self):
        global logged_in_user_name
        emp_id = self.employee_id.text()
        pwd = self.password.text()

        if not emp_id or not pwd:
            self.show_warning("인증 실패", "사번과 비밀번호를 모두 입력해주세요.")
            return

        success, message, user_name = authenticate_user(emp_id, pwd)
        if success:
            logged_in_user_name = user_name
            self.stacked_widget.widget(1).update_welcome_message() 
            self.show_info(" ", f"'{user_name}'님 환영합니다!")
            self.stacked_widget.setCurrentIndex(1)
        else:
            if message == "Verification needed":
                self.show_warning("인증 오류", "비밀번호가 일치하지 않습니다.")
            elif message == "Registration needed":
                self.show_warning("인증 오류", "해당 사번은 등록되지 않았습니다.")

    def show_info(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Info")
        
    def show_warning(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Warning")

# [RegistrationWidget]
class RegistrationWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        card_frame = QFrame()
        card_frame.setFixedSize(450, 500)
        card_frame.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 20px; }")
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(50, 40, 50, 40)
        card_layout.setSpacing(15)

        title = QLabel("직원 회원가입")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Malgun Gothic', 18, QFont.Bold))
        title.setStyleSheet("color: #E88D83;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("사용자 이름")
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setPlaceholderText("사번")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("비밀번호")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("비밀번호 확인")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        register_btn = QPushButton("회원가입 완료")
        register_btn.setObjectName("PrimaryButton")
        register_btn.clicked.connect(self.handle_registration)
        
        back_btn = QPushButton("로그인 화면으로 돌아가기")
        back_btn.setObjectName("SignupButton") 
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        card_layout.addWidget(title)
        card_layout.addSpacing(30)
        card_layout.addWidget(self.name_input)
        card_layout.addWidget(self.employee_id_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.confirm_password_input)
        card_layout.addSpacing(20)
        card_layout.addWidget(register_btn)
        card_layout.addStretch(1)
        card_layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(card_frame)
        h_layout.addStretch(1)
        
        main_layout = QVBoxLayout(self)
        main_layout.addStretch(1)
        main_layout.addLayout(h_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def handle_registration(self):
        name = self.name_input.text()
        emp_id = self.employee_id_input.text()
        pwd = self.password_input.text()
        pwd_confirm = self.confirm_password_input.text()

        if not name or not emp_id or not pwd or not pwd_confirm:
            self.show_warning("입력 오류", "모든 필드를 채워주세요.")
            return

        if pwd != pwd_confirm:
            self.show_warning("비밀번호 오류", "비밀번호가 일치하지 않습니다.")
            return

        success, message = register_user(name, emp_id, pwd)

        if success:
            self.show_info("성공", message + "\n로그인 화면으로 돌아갑니다.")
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.show_error("등록 오류", message)
            
    def show_info(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Info")
    def show_warning(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Warning")
    def show_error(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Critical")


# ---------------------------------------------------------
# 06. 메뉴 화면
# ---------------------------------------------------------
class MainWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()
        self.update_welcome_message() 

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)

        header_layout = QHBoxLayout()
        self.welcome_label = QLabel("반갑습니다. OOO님")
        self.welcome_label.setFont(QFont('Hakgyoansim Boadmarker R', 20, QFont.Bold))
        self.welcome_label.setStyleSheet("color: #333333;")
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch(1) 
        
        logout_btn = QPushButton("로그아웃")
        logout_btn.setObjectName("LogoutButton")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        main_layout.addLayout(header_layout)

        self.grid_widget = QWidget()
        grid_layout = QGridLayout(self.grid_widget)
        grid_layout.setSpacing(25)

        menu_items = [
            "환자 등록/조회", " ", " ", " ",
            " ", " ", " ", "시스템 설정"
        ]
        self.menu_buttons = []

        for i, text in enumerate(menu_items):
            btn = QPushButton(text)
            btn.setObjectName("MenuButton")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.menu_buttons.append(btn)
            
            if text == "환자 등록/조회":
                btn.setProperty("enabled", True)
                btn.setStyleSheet('QPushButton#MenuButton { background-color: #FFFDFC; }')
                btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
            elif text == "시스템 설정":
                btn.setProperty("enabled", True)
                btn.setStyleSheet('QPushButton#MenuButton { background-color: #FFFDFC; }')
                btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
            else:
                btn.setEnabled(False)
                btn.setProperty("enabled", False)
                btn.setText("")
                
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 30))
            btn.setGraphicsEffect(shadow)
                
            row = i // 4
            col = i % 4
            grid_layout.addWidget(btn, row, col)

        main_layout.addWidget(self.grid_widget)
        main_layout.addStretch(1)

    def update_welcome_message(self):
        global logged_in_user_name
        self.welcome_label.setText(f"반갑습니다. {logged_in_user_name}님")
        
    def logout(self):
        global logged_in_user_name
        logged_in_user_name = "Guest"
        self.stacked_widget.setCurrentIndex(0)

# ---------------------------------------------------------
# 07. 환자 등록/조회 화면
# ---------------------------------------------------------
class PatientWidget(QWidget):
    def __init__(self, stacked_widget, serial_listener):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_listener = serial_listener
        self.current_cardnumber = None 
        self.age_numeric = None
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        card_frame = QFrame()
        card_frame.setMinimumWidth(600)
        card_frame.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 20px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 36))
        card_frame.setGraphicsEffect(shadow)
        
        card_main_layout = QVBoxLayout(card_frame)
        card_main_layout.setContentsMargins(30, 20, 30, 30)
        card_main_layout.setSpacing(10)

        inner_header_layout = QHBoxLayout()
        inner_header_layout.addStretch(1)
        close_btn = QPushButton("X")
        close_btn.setFixedSize(QSize(30, 30))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setObjectName("CloseButton") # 스타일 적용
        close_btn.clicked.connect(self.close_screen)
        inner_header_layout.addWidget(close_btn)
        card_main_layout.addLayout(inner_header_layout)

        card_title = QLabel("환자 조회 및 등록 시스템")
        card_title.setAlignment(Qt.AlignCenter)
        card_title.setFont(QFont('Hakgyoansim Boadmarker R', 16, QFont.Bold))
        card_title.setStyleSheet("color: #E88D83; border: none; background-color: transparent;")
        card_main_layout.addWidget(card_title)
        card_main_layout.addSpacing(10)

        card_grid_layout = QGridLayout()
        card_grid_layout.setSpacing(20)
        card_main_layout.addLayout(card_grid_layout)

        self.fields = {}
        labels = ["등록번호", "이름", "주민번호", "생년월일", "(만) 나이", "성별", "전화번호"]
        
        self.gender_group = None 
        self.radio_male = None
        self.radio_female = None

        for i, text in enumerate(labels):
            label = QLabel(text)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            card_grid_layout.addWidget(label, i, 0)
            
            if text == "성별":
                gender_layout = QHBoxLayout()
                self.radio_male = QRadioButton("남")
                self.radio_female = QRadioButton("여")
                self.radio_male.setAutoExclusive(False)
                self.radio_female.setAutoExclusive(False)
                self.radio_male.clicked.connect(lambda: self.check_gender_toggle(self.radio_male))
                self.radio_female.clicked.connect(lambda: self.check_gender_toggle(self.radio_female))
                gender_layout.addWidget(self.radio_male)
                gender_layout.addSpacing(20)
                gender_layout.addWidget(self.radio_female)
                gender_layout.addStretch(1)
                card_grid_layout.addLayout(gender_layout, i, 1)
            else:
                line_edit = QLineEdit()
                line_edit.setMinimumHeight(40)
                line_edit.setObjectName("NoBorder")
                card_grid_layout.addWidget(line_edit, i, 1)
                self.fields[text] = line_edit
                
                if text == "등록번호":
                    clear_btn = QPushButton("지우기")
                    clear_btn.setObjectName("TertiaryButton") 
                    clear_btn.setFixedSize(QSize(70, 35))
                    clear_btn.clicked.connect(self.clear_fields)
                    card_grid_layout.addWidget(clear_btn, i, 2, 1, 1, Qt.AlignLeft)
                elif text == "이름":
                    update_btn = QPushButton("수정")
                    update_btn.setObjectName("SecondaryButton")
                    update_btn.setFixedSize(QSize(70, 35))
                    update_btn.clicked.connect(self.update_patient)
                    card_grid_layout.addWidget(update_btn, i, 2, 1, 1, Qt.AlignLeft)
                elif text == "성별":
                    add_btn = QPushButton("추가")
                    add_btn.setObjectName("SecondaryButton")
                    add_btn.setFixedSize(QSize(70, 35))
                    add_btn.clicked.connect(self.add_patient_data)
                    card_grid_layout.addWidget(add_btn, i, 2, 1, 1, Qt.AlignLeft)

        self.Ernumber = self.fields['등록번호']
        self.Ename = self.fields['이름']
        self.Eresident = self.fields['주민번호']
        self.Ebirth = self.fields['생년월일']
        self.Eage = self.fields['(만) 나이']
        self.Ephone = self.fields['전화번호']

        self.Eage.setReadOnly(True) 
        
        last_row = len(labels)
        search_btn = QPushButton("조회")
        search_btn.setObjectName("SearchButton")
        search_btn.setFixedSize(QSize(70, 40))
        search_btn.clicked.connect(self.search)
        
        register_btn = QPushButton("등록")
        register_btn.setObjectName("PrimaryButton")
        register_btn.setFixedSize(QSize(70, 40))
        register_btn.clicked.connect(self.register_patient)
        
        card_grid_layout.addWidget(search_btn, last_row, 1, 1, 1, Qt.AlignRight)
        card_grid_layout.addWidget(register_btn, last_row, 2, 1, 1, Qt.AlignLeft)

        main_form_layout = QVBoxLayout()
        main_form_layout.addWidget(card_frame)

        center_layout = QHBoxLayout()
        center_layout.addStretch(1)
        center_layout.addLayout(main_form_layout)
        center_layout.addStretch(1)
        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)

        self.Ebirth.textChanged.connect(self.format_birth)
        self.Ebirth.editingFinished.connect(self.calculate_age)
        self.Ephone.textChanged.connect(self.format_phone)
        self.Eresident.textChanged.connect(self.format_resident_number)

    def connect_signals(self):
        if self.serial_listener:
            self.serial_listener.card_detected_signal.connect(self.card_detected)
            
    # --- 데이터 처리 로직 ---
    def show_info(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Info")
    def show_warning(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Warning")
    def show_error(self, title, message):
        CustomMessageBox.show_message(self, title, message, "Critical")
    def ask_yes_no(self, title, message):
        return CustomMessageBox.ask_yes_no(self, title, message)
    
    def close_screen(self):
        self.clear_fields()
        self.stacked_widget.setCurrentIndex(1)
        
    def check_gender_toggle(self, clicked_btn):
        if clicked_btn.isChecked():
            if clicked_btn == self.radio_male:
                self.radio_female.setChecked(False)
            else:
                self.radio_male.setChecked(False)
    
    def get_gender(self):
        if self.radio_male.isChecked(): return "남"
        elif self.radio_female.isChecked(): return "여"
        return None
    
    def set_gender(self, gender):
        if gender == '남':
            self.radio_male.setChecked(True)
            self.radio_female.setChecked(False)
        elif gender == '여':
            self.radio_male.setChecked(False)
            self.radio_female.setChecked(True)
        else:
            self.radio_male.setChecked(False)
            self.radio_female.setChecked(False)
            
    # --- 데이터 포맷팅 ---
    def format_birth(self):
        fbirth = self.Ebirth.text().replace("-", "")
        cursor_pos = self.Ebirth.cursorPosition()
        formatted_date = ""
        
        if len(fbirth) > 4:
            formatted_date = fbirth[:4] + "-"
            if len(fbirth) > 6:
                formatted_date += fbirth[4:6] + "-" + fbirth[6:8]
            else:
                formatted_date += fbirth[4:]
        else:
            formatted_date = fbirth
        
        new_cursor_pos = cursor_pos
        current_text = self.Ebirth.text()
        self.Ebirth.blockSignals(True)
        self.Ebirth.setText(formatted_date)
        self.Ebirth.blockSignals(False)

        if len(formatted_date) > len(current_text):
             new_cursor_pos += (len(formatted_date) - len(current_text))
        elif len(formatted_date) < len(current_text):
             new_cursor_pos -= (len(current_text) - len(formatted_date))
        self.Ebirth.setCursorPosition(min(new_cursor_pos, len(formatted_date)))
        
    def calculate_age(self):
        global age_numeric
        try:
            birth_date_str = self.Ebirth.text()
            if not birth_date_str:
                self.Eage.setText("")
                self.age_numeric = None
                return

            if len(birth_date_str) < 10 or birth_date_str.count('-') != 2:
                self.Eage.setText("형식 오류")
                self.age_numeric = None
                return
            
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
            today = datetime.today()

            if birth_date > today:
                self.Eage.setText("유효하지 않음")
                self.age_numeric = None
                return

            total_months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
            if today.day < birth_date.day:
                total_months -= 1

            years = total_months // 12
            months = total_months % 12

            self.age_numeric = years
            age_numeric = years

            if years < 3:
                age_text = f"{years}살 {months}개월"
            else:
                age_text = f"(만) {years}세"

            self.Eage.setText(age_text)
        except ValueError:
            self.Eage.setText("")
            self.age_numeric = None
            
    def format_phone(self):
        phone = self.Ephone.text().replace("-", "")
        formatted_phone = ""
        if len(phone)>3:
            formatted_phone = phone[:3] + "-"
            if len(phone) > 7:
                formatted_phone += phone[3:7] + "-" + phone[7:11]
            else:
                formatted_phone += phone[3:]
        else:
            formatted_phone = phone
            
        cursor_pos = self.Ephone.cursorPosition()
        current_text = self.Ephone.text()
        self.Ephone.blockSignals(True)
        self.Ephone.setText(formatted_phone)
        self.Ephone.blockSignals(False)

        new_cursor_pos = cursor_pos
        if len(formatted_phone) > len(current_text):
             new_cursor_pos += (len(formatted_phone) - len(current_text))
        elif len(formatted_phone) < len(current_text):
             new_cursor_pos -= (len(current_text) - len(formatted_phone))
        self.Ephone.setCursorPosition(min(new_cursor_pos, len(formatted_phone)))

    def format_resident_number(self):
        text = self.Eresident.text().replace("-", "")
        formatted_text = ""
        if len(text) > 6:
            formatted_text = text[:6] + "-" + text[6:]
        else:
            formatted_text = text
            
        if len(formatted_text) > 14:
            formatted_text = formatted_text[:14]

        cursor_pos = self.Eresident.cursorPosition()
        current_text = self.Eresident.text()

        self.Eresident.blockSignals(True)
        self.Eresident.setText(formatted_text)
        self.Eresident.blockSignals(False)

        new_cursor_pos = cursor_pos
        if len(formatted_text) > len(current_text):
             new_cursor_pos += (len(formatted_text) - len(current_text))
        elif len(formatted_text) < len(current_text):
            new_cursor_pos -= (len(current_text) - len(formatted_text))
        self.Eresident.setCursorPosition(min(new_cursor_pos, len(formatted_text)))

        # 생년월일/성별 자동 입력
        clean_rrn = formatted_text.replace("-", "")
        if len(clean_rrn) >= 7:
            rrn_front = clean_rrn[:6]
            gender_digit = clean_rrn[6]
            
            if gender_digit in ['1', '3']:
                self.set_gender("남")
            elif gender_digit in ['2', '4']:
                self.set_gender("여")
            
            if rrn_front.isdigit():
                year_prefix = ""
                if gender_digit in ['1', '2']: year_prefix = "19"
                elif gender_digit in ['3', '4']: year_prefix = "20"
                
                if year_prefix:
                    full_year = year_prefix + rrn_front[:2]
                    month = rrn_front[2:4]
                    day = rrn_front[4:6]
                    if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
                        birth_date = f"{full_year}-{month}-{day}"
                        if self.Ebirth.text() != birth_date:
                            self.Ebirth.setText(birth_date)
                            self.calculate_age()

    # --- CRUD 및 시리얼 로직 ---
    def get_next_patient_number(self):
        conn = connect_to_database()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(registrationnumber) FROM patients_l")
            result = cursor.fetchone()
            max_num_str = result[0]
            if max_num_str and max_num_str.isdigit():
                 next_number = int(max_num_str) + 1
            else:
                 next_number = 1
        except Exception as e:
            print(f"등록번호 조회 중 오류 발생: {e}")
            next_number = 1
        finally:
            cursor.close()
            conn.close()
        return f"{next_number:08d}"

    def card_detected(self, cardnumber):
        cardnumber = cardnumber.strip()
        print(f"카드 인식 슬롯 호출됨: [{cardnumber}]")
        
        if self.stacked_widget.currentWidget() != self:
             self.serial_listener.set_processing_done()
             return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients_l WHERE cardnumber = ?", (cardnumber,))
            result = cursor.fetchone()

            if result:
                self.display_patient_info(result)
                self.show_info("카드 인식", "등록된 환자 정보가 표시되었습니다.")
                self.current_cardnumber = cardnumber
            else:
                response = self.ask_yes_no("카드 등록", "새로운 카드입니다. 등록하시겠습니까?")
                if response:
                    self.clear_fields() 
                    self.current_cardnumber = cardnumber
                    registrationnumber = self.get_next_patient_number()
                    self.Ernumber.setText(registrationnumber)
                    self.show_info("카드 등록", "새로운 카드가 등록되었습니다. 환자 정보를 입력하고 [등록] 버튼을 누르세요.")
                else:
                    self.show_info("취소", "카드 등록이 취소되었습니다.")
            cursor.close()
            conn.close()
        except Exception as e:
            self.show_error("오류", f"카드 처리 중 문제가 발생했습니다: {e}")
        finally:
            self.serial_listener.set_processing_done()

    def clear_fields(self):
        self.Ernumber.clear()
        self.Ename.clear()
        self.Eresident.clear()
        self.Ebirth.clear()
        self.Eage.clear()
        self.Ephone.clear()
        self.set_gender(None)
        
        global age_numeric
        age_numeric = None
        self.current_cardnumber = None
        self.age_numeric = None

    def display_patient_info(self, result):
        self.clear_fields()
        id_, cardnumber, registrationnumber, name, residentnumber, fbirth, age_display, gender, phonenumber = result
        self.Ernumber.setText(registrationnumber or "")
        self.Ename.setText(name or "")
        self.Eresident.setText(residentnumber or "") 
        self.Ebirth.setText(fbirth or "")
        self.Ephone.setText(phonenumber or "")
        self.set_gender(gender)
        self.current_cardnumber = cardnumber 
        
        if fbirth:
            self.calculate_age()
        else:
            self.Eage.setText("-")
            self.age_numeric = None

    def update_patient(self):
        registrationnumber = self.Ernumber.text()
        name = self.Ename.text()
        residentnumber = self.Eresident.text() 
        dateofbirth = self.Ebirth.text()
        phonenumber = self.Ephone.text()
        gender = self.get_gender()
        age = self.age_numeric 

        if not registrationnumber:
            self.show_warning("변경 오류", "등록번호는 필수입니다.")
            return

        conn = connect_to_database()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE patients_l SET name=?, residentnumber=?, fbirth=?, age=?, gender=?, phonenumber=? WHERE registrationnumber=?",
                (name or None, residentnumber or None, dateofbirth or None, age or None, gender or None, phonenumber or None, registrationnumber)
            )
            conn.commit()
            self.show_info("성공", "환자 정보가 변경되었습니다!")
            self.clear_fields()
        except Exception as e:
            self.show_error("데이터베이스 오류", f"오류 발생: {e}")
        finally:
            cursor.close()
            conn.close()

    def add_patient_data(self):
        registrationnumber = self.Ernumber.text()
        name = self.Ename.text()
        residentnumber = self.Eresident.text()
        dateofbirth = self.Ebirth.text()
        phonenumber = self.Ephone.text()
        gender = self.get_gender()
        
        age = None
        if dateofbirth:
            self.calculate_age()
            age = self.age_numeric

        if not registrationnumber:
            self.show_warning("추가 오류", "등록번호는 필수입니다.")
            return

        conn = connect_to_database()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM patients_l WHERE registrationnumber = ?", (registrationnumber,))
            result = cursor.fetchone()
            if not result:
                self.show_warning("추가 오류", "해당 등록번호의 환자가 존재하지 않습니다.")
                return
            
            update_fields = []
            update_values = []
            
            if not result[3] and name:
                 update_fields.append("name=?")
                 update_values.append(name)
            if not result[4] and residentnumber:
                 update_fields.append("residentnumber=?")
                 update_values.append(residentnumber)
            if not result[5] and dateofbirth:
                update_fields.append("fbirth=?")
                update_values.append(dateofbirth)
            if not result[6] and age:
                update_fields.append("age=?")
                update_values.append(age)
            if not result[7] and gender:
                 update_fields.append("gender=?")
                 update_values.append(gender)
            if not result[8] and phonenumber:
                update_fields.append("phonenumber=?")
                update_values.append(phonenumber)

            if update_fields:
                update_values.append(registrationnumber)
                sql = "UPDATE patients_l SET " + ", ".join(update_fields) + " WHERE registrationnumber=?"
                cursor.execute(sql, tuple(update_values))
                conn.commit()
                self.show_info("성공", "환자 정보가 추가되었습니다!")
            else:
                self.show_info("정보 없음", "추가할 데이터가 없습니다.")

        except Exception as e:
            self.show_error("데이터베이스 오류", f"오류 발생: {e}")
        finally:
            cursor.close()
            conn.close()
        self.clear_fields()

    def search(self):
        patient_number = self.Ernumber.text()
        if patient_number:
            conn = connect_to_database()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM patients_l WHERE registrationnumber = ?", (patient_number,))
                result = cursor.fetchone()
                if result:
                    self.display_patient_info(result)
                else:
                    self.show_warning("조회 실패", "해당 번호의 환자가 없습니다.")
            except Exception as e:
                 self.show_error("데이터베이스 오류", f"조회 중 오류 발생: {e}")
            finally:
                cursor.close()
                conn.close()

    def register_patient(self):
        registrationnumber = self.Ernumber.text()
        name = self.Ename.text()
        residentnumber = self.Eresident.text()
        dateofbirth = self.Ebirth.text()
        phonenumber = self.Ephone.text()
        gender = self.get_gender()
        cardnumber = self.current_cardnumber

        age = None
        if dateofbirth:
            self.calculate_age()
            age = self.age_numeric

        if not registrationnumber:
            self.show_warning("등록 오류", "등록번호는 필수입니다.")
            return

        if not cardnumber:
            self.show_warning("등록 오류", "카드번호가 없습니다. 카드를 먼저 인식시켜 주세요.")
            return

        conn = connect_to_database()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO patients_l (cardnumber, registrationnumber, name, residentnumber, fbirth, age, gender, phonenumber) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (cardnumber, registrationnumber, name or None, residentnumber or None, dateofbirth or None, age or None, gender or None, phonenumber or None)
            )
            conn.commit()
            self.show_info("성공", "환자 정보가 등록되었습니다!")
            self.clear_fields()
        except sqlite3.IntegrityError:
            self.show_error("등록 오류", "이미 존재하는 등록번호입니다.")
        except Exception as e:
            self.show_error("데이터베이스 오류", f"오류 발생: {e}")
        finally:
            cursor.close()
            conn.close()

# ---------------------------------------------------------
# 08. 시스템 설정 화면
# ---------------------------------------------------------
class SystemSettingsWidget(QWidget):
    def __init__(self, stacked_widget, serial_listener=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.serial_listener = serial_listener 
        self.init_ui()
        
    def init_ui(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        card_frame = QFrame()
        card_frame.setFixedSize(600, 500)
        card_frame.setObjectName("SystemCardFrame") 
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 36))
        card_frame.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        header_layout.addStretch(1)
        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseButton")
        close_btn.setFixedSize(QSize(30, 30))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1)) 
        header_layout.addWidget(close_btn)
        card_layout.addLayout(header_layout)
        
        title = QLabel("시스템 설정")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Hakgyoansim Boadmarker R', 22, QFont.Bold))
        title.setStyleSheet("color: #E88D83; border: none; background-color: transparent;")
        card_layout.addWidget(title)
        card_layout.addSpacing(20)
        
        desc_label = QLabel("아두이노가 연결된 포트를 선택해주세요.")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #666666; font-size: 14px; border: none;")
        card_layout.addWidget(desc_label)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumHeight(40)
        self.port_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        control_layout.addWidget(self.port_combo)

        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setObjectName("RefreshButton")
        self.refresh_btn.setFixedSize(80, 40)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        control_layout.addWidget(self.refresh_btn)
        card_layout.addLayout(control_layout)

        self.connect_btn = QPushButton("연결 설정 적용")
        self.connect_btn.setObjectName("ConnectButton")
        self.connect_btn.setMinimumHeight(50)
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self.connect_arduino)
        card_layout.addWidget(self.connect_btn)

        self.status_label = QLabel("현재 상태: 대기 중")
        self.status_label.setObjectName("StatusLabel") 
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-size: 13px; margin-top: 10px; border: none;")
        card_layout.addWidget(self.status_label)
        card_layout.addStretch(1)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch(1)
        center_layout.addWidget(card_frame)
        center_layout.addStretch(1)
        main_layout.addLayout(center_layout)

        self.refresh_ports()

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            self.port_combo.addItem("연결된 포트 없음")
            self.connect_btn.setEnabled(False)
            self.status_label.setText("연결 가능한 포트가 없습니다.")
            return

        self.connect_btn.setEnabled(True)
        for port in ports:
            display_text = f"{port.device} ({port.description})"
            self.port_combo.addItem(display_text, port.device)
            
        self.status_label.setText(f"{len(ports)}개의 포트가 검색되었습니다.")

    def connect_arduino(self):
        selected_port = self.port_combo.currentData()
        if not selected_port: return

        if self.serial_listener:
            try:
                if self.serial_listener.arduino and self.serial_listener.arduino.is_open:
                    self.serial_listener.arduino.close()

                baud = getattr(self.serial_listener, 'baudrate', 115200)
                
                self.serial_listener.arduino = serial.Serial(selected_port, baud, timeout=.1)
                
                self.status_label.setText(f"성공: {selected_port}에 연결되었습니다.")
                self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; margin-top: 10px; border: none;") 
                QMessageBox.information(self, "연결 성공", f"포트가 {selected_port}로 변경되었습니다.")
                
            except Exception as e:
                self.status_label.setText(f"오류: {str(e)}")
                self.status_label.setStyleSheet("color: #FF5252; font-weight: bold; margin-top: 10px; border: none;")
                QMessageBox.critical(self, "연결 실패", f"포트 연결 중 오류가 발생했습니다.\n{str(e)}")
        else:
            self.status_label.setText(f"설정됨: {selected_port} (실제 연결 객체 없음)")
            QMessageBox.information(self, "설정 저장", f"선택한 포트: {selected_port}\n(MainApp에서 serial_listener를 전달해야 실제 동작합니다)")

# ---------------------------------------------------------
# f. 설정
# ---------------------------------------------------------
class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("병원 정보 시스템")
        self.setGeometry(100, 100, 1200, 800)
        
        self.serial_listener = SerialListener(port='COM5', baudrate=115200)

        # 2. QTimer
        self.timer = QTimer(self)
        if self.serial_listener:
            self.timer.timeout.connect(self.serial_listener.read_from_arduino)
        self.timer.start(100)
        
        # 3. 화면 구성
        self.stacked_widget = QStackedWidget()
        
        self.login_widget = LoginWidget(self.stacked_widget)
        self.main_menu_widget = MainWidget(self.stacked_widget)
        self.patient_widget = PatientWidget(self.stacked_widget, self.serial_listener) 
        self.registration_widget = RegistrationWidget(self.stacked_widget) 
        self.system_settings_widget = SystemSettingsWidget(self.stacked_widget, self.serial_listener) 
        
        self.stacked_widget.addWidget(self.login_widget)           # Index 0
        self.stacked_widget.addWidget(self.main_menu_widget)       # Index 1
        self.stacked_widget.addWidget(self.patient_widget)         # Index 2
        self.stacked_widget.addWidget(self.registration_widget)    # Index 3
        self.stacked_widget.addWidget(self.system_settings_widget) # Index 4

        self.stacked_widget.setCurrentIndex(0)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        
        self.setStyleSheet(QSS_STYLE)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    font_id = QFontDatabase.addApplicationFont("Hakgyoansim_BoardmarkerR.ttf")
    loaded_fonts = QFontDatabase.applicationFontFamilies(font_id)


    window = MainApp()
    window.show()
    sys.exit(app.exec_())
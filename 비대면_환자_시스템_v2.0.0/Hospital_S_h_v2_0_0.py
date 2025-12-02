import serial
from tkinter import *
from tkinter import messagebox
import sqlite3
from datetime import datetime
import os

#--기본설정------
tk = Tk()
tk.geometry("800x800")
tk.title('환자등록/조회시스템')

age_numeric = None

#시리얼통신
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1)

last_cardnumber = ''
card_processing = False

DB_FILE = "patient_db.sqlite3"

#SQLite DB 연결
def connect_to_database():
    conn = sqlite3.connect(DB_FILE)
    return conn

#DB 초기화(파일 없으면 생성)
def initialize_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients_l (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cardnumber TEXT,
            registrationnumber TEXT UNIQUE,
            name TEXT,
            fbirth TEXT,
            age INTEGER,
            gender TEXT,
            phonenumber TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# 프로그램 시작 전에 DB 초기화
initialize_database()

"""
#--기본설정------
tk = Tk()
tk.geometry("800x800")
tk.title('환자등록/조회시스템')

age_numeric = None

#시리얼통신
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1)

last_cardnumber = ''
card_processing = False

#mysql
def connect_to_database():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="0000",
        database="patient_db"
    )
    """

#형식설정
#생년월일
def format_birth(event):

    
    fbirth = Ebirth.get().replace("-", "")
    if event.keysym == "BackSpace":
        return

    formatted_date = ""
    if len(fbirth) >= 4:
        formatted_date = fbirth[:4] + "-"
        if len(fbirth) >= 6:
            formatted_date += fbirth[4:6] + "-"
            formatted_date += fbirth[6:8]
        else:
            formatted_date += fbirth[4:]
    else:
        formatted_date = fbirth

    Ebirth.delete(0, END)
    Ebirth.insert(0, formatted_date)

#만나이
def calculate_age():
    global age_numeric
    try:           
        birth_date_str = Ebirth.get()
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.today()

        if None == Ebirth.get():
            age_numeric = None

        if birth_date > today:
            Eage.delete(0, END)
            Eage.insert(0, "유효하지 않은 생년월일")
            age_numeric = None 
            return
        
        

        total_months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
        if today.day < birth_date.day:
            total_months -= 1

        years = total_months // 12
        months = total_months % 12

        age_numeric = years  

        if years < 3:
            age_text = f"{years}살 {months}개월"
        else:
            age_text = f"(만) {years}살"

        Eage.delete(0, END)
        Eage.insert(0, age_text)
    except ValueError:
        Eage.delete(0, END)
        Eage.insert(0, "")
        age_numeric = None  

#전화번호
def format_phone(event):
    phone = Ephone.get().replace("-", "")
    if event.keysym == "BackSpace":
        return  

    formatted_phone = ""
    if len(phone) >= 3:
        formatted_phone = phone[:3] + "-"
        if len(phone) >= 7:
            formatted_phone += phone[3:7] + "-"
            formatted_phone += phone[7:11]
        else:
            formatted_phone += phone[3:]
    else:
        formatted_phone = phone

    Ephone.delete(0, END)
    Ephone.insert(0, formatted_phone)


def is_valid_cardnumber(data):
    if data.startswith("4:") and len(data) > 10:
        return True
    else:
        return False

def card_detected(cardnumber):
    global card_processing
    cardnumber = cardnumber.strip()
    print(f"인식된 카드번호: [{cardnumber}]")  
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM patients_l WHERE cardnumber = ?", (cardnumber,))
    result = cursor.fetchone()

    if result:
        display_patient_info(result)
        messagebox.showinfo("카드 인식", "등록된 환자 정보가 표시되었습니다.")
    else:
        response = messagebox.askyesno("카드 등록", "새로운 카드입니다. 등록하시겠습니까?")
        if response:
            global current_cardnumber
            current_cardnumber = cardnumber
            clear_fields()

            setup_patient_info_screen()

            registrationnumber = get_next_patient_number()
            Ernumber.delete(0, END)
            Ernumber.insert(0, registrationnumber)

            messagebox.showinfo("카드 등록", "새로운 카드가 등록되었습니다. 환자 정보를 입력하세요.")
        else:
            messagebox.showinfo("취소", "카드 등록이 취소되었습니다.")

    cursor.close()
    connection.close()

    card_processing = False
  

#엔트리를 지우기
def clear_fields():
    global genderh
    Ernumber.delete(0, END)
    Ename.delete(0, END)
    Ebirth.delete(0, END)
    Eage.delete(0, END)
    Ephone.delete(0, END)
    genderh.set(' ')


def delete_fields():
    global genderh
    Ernumber.delete(0, END)
    Ename.delete(0, END)
    Ebirth.delete(0, END)
    Eage.delete(0, END)
    Ephone.delete(0, END)
    genderh.set(' ')



#조회된 값을 가져오기
def display_patient_info(result):
    clear_fields()
    id_, cardnumber, registrationnumber, name, fbirth, age, gender, phonenumber = result

    Ernumber.insert(0, registrationnumber or "")
    Ename.insert(0, name or "")
    Ebirth.insert(0, fbirth or "")  # fbirth 컬럼 사용
    Eage.insert(0, age or "")
    Ephone.insert(0, phonenumber or "")

    if gender == '남':
        genderh.set("남")
    elif gender == "여":
        genderh.set("여")
    else:
        genderh.set(' ')

                # 생년월일이 있으면 나이 계산

    if fbirth:
        Ebirth.delete(0, END)
        Ebirth.insert(0, fbirth)
        calculate_age()

    else:
        Eage.delete(0, END)
        Eage.insert(0, "-")
        age_numeric = None

#업데이트 하기
def update_patient():
    global gender_var, age_numeric, current_cardnumber

    registrationnumber = Ernumber.get()
    name = Ename.get()
    dateofbirth = Ebirth.get()
    phonenumber = Ephone.get()
    gender = genderh.get()
    age = age_numeric

    if not registrationnumber:
        messagebox.showwarning("변경 오류", "등록번호는 필수입니다.")
        return

    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE patients_l SET name=?, dateofbirth=?, age=?, gender=?, phonenumber=? WHERE registrationnumber=?",
            (
                name or None,
                dateofbirth or None,
                age or None ,
                gender or None,
                phonenumber or None,
                registrationnumber
            )
        )
        connection.commit()
    except Exception as e:
        messagebox.showerror("데이터베이스 오류", f"오류 발생: {e}")
        return
    finally:
        cursor.close()
        connection.close()

    messagebox.showinfo("성공", "환자 정보가 변경되었습니다!")
    clear_fields()


#데이터를 추가하기
def add_patient_data():
    global gender_var, age_numeric

    registrationnumber = Ernumber.get()
    name = Ename.get()
    dateofbirth = Ebirth.get()
    phonenumber = Ephone.get()
    gender = genderh.get()

    if dateofbirth:
        calculate_age()
        if age_numeric is None:
            messagebox.showwarning("추가 오류", "생년월일을 올바르게 입력하여 나이를 계산해 주세요.")
            return
        age = age_numeric
    else:
        age = None

    if not registrationnumber:
        messagebox.showwarning("추가 오류", "등록번호는 필수입니다.")
        return

    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM patients_l WHERE registrationnumber = ?", (registrationnumber,))
        result = cursor.fetchone()
        if not result:
            messagebox.showwarning("추가 오류", "해당 등록번호의 환자가 존재하지 않습니다.")
            return

        update_fields = []
        update_values = []

        if not result[2] and name:
            update_fields.append("name=?")
            update_values.append(name)
        if not result[3] and dateofbirth:
            update_fields.append("dateofbirth=?")
            update_values.append(dateofbirth)
            update_fields.append("age=?")
            update_values.append(age)
        if not result[4] and age is not None:
            update_fields.append("age=?")
            update_values.append(age)
        if not result[5] and gender:
            update_fields.append("gender=?")
            update_values.append(gender)
        if not result[6] and phonenumber:
            update_fields.append("phonenumber=?")
            update_values.append(phonenumber)

        if update_fields:
            update_values.append(registrationnumber)
            sql = "UPDATE patients_l SET " + ", ".join(update_fields) + " WHERE registrationnumber=?"
            cursor.execute(sql, tuple(update_values))
            connection.commit()
            messagebox.showinfo("성공", "환자 정보가 추가되었습니다!")
        else:
            messagebox.showinfo("정보 없음", "추가할 데이터가 없습니다. 모든 필드가 이미 채워져 있습니다.")

    except Exception as e:
        messagebox.showerror("데이터베이스 오류", f"오류 발생: {e}")
    finally:
        cursor.close()
        connection.close()

    clear_fields()       
        
# 환자 정보 화면 설정 함수
def setup_patient_info_screen():
    global Ernumber, Ename, Ebirth, Eage, Egender_1, Egender_2, genderh, Ephone

    if 'Ernumber' in globals():
        return
   

    mtitle = Label(tk, text='환자등록/조회서비스', font=("Arial", 40, "bold"))
    mtitle.place(x=150, y=50)


    pynumber = Label(tk, text='등록번호', font=("Arial", 20))
    pynumber.place(x=180, y=120)
    Ernumber = Entry(tk)
    Ernumber.place(x=350, y=120, height=30)

    pyname = Label(tk, text='이름', font=("Arial", 20))
    pyname.place(x=180, y=170)
    Ename = Entry(tk)
    Ename.place(x=350, y=170, height=30)

    pybirth = Label(tk, text='생년월일', font=("Arial", 20))
    pybirth.place(x=180, y=220)
    Ebirth = Entry(tk)
    Ebirth.place(x=350, y=220, height=30)
    Ebirth.bind("<KeyRelease>", format_birth)
    Ebirth.bind("<FocusOut>", lambda event: calculate_age())
    

    pyage = Label(tk, text='(만)나이', font=("Arial", 20))
    pyage.place(x=180, y=270)
    Eage = Entry(tk)
    Eage.place(x=350, y=270, height=30)


    genderh = StringVar(master=tk, value=" ")
    pygender = Label(tk, text='성별', font=("Arial", 20))
    pygender.place(x=180, y=320)
    Egender_1 = Radiobutton(tk, variable=genderh, text='남', value="남")
    Egender_1.place(x=350, y=320)
    Egender_2 = Radiobutton(tk, variable=genderh,text='여', value="여")
    Egender_2.place(x=400, y=320)

    pyphone = Label(tk, text='전화번호', font=("Arial", 20))
    pyphone.place(x=180, y=370)
    Ephone = Entry(tk)
    Ephone.place(x=350, y=370, height=30)
    Ephone.bind("<KeyRelease>", format_phone)

    
    etn = Button(tk, text="등록", command=register_patient, font=("Arial", 15))
    etn.place(x=200, y=450)

    add_data_btn = Button(tk, text="추가", command=add_patient_data, font=("Arial", 15))
    add_data_btn.place(x=300,  y=450)

    update_btn = Button(tk, text="변경", command=update_patient, font=("Arial", 15))
    update_btn.place(x=400,  y=450)

    ser = Button(tk, text="조회", command=search, font=("Arial", 15))
    ser.place(x=500, y=450)

    
    delete_btn = Button(tk, text="삭제", command=delete_fields, font=("Arial", 15))
    delete_btn.place(x=600, y=450)


#데이터를 등록하기
def register_patient():
    global gender_var, age_numeric, current_cardnumber
    registrationnumber = Ernumber.get()
    name = Ename.get()
    dateofbirth = Ebirth.get()
    phonenumber = Ephone.get()
    gender = genderh.get()
    age = age_numeric


    if registrationnumber:
        connection = connect_to_database()
        cursor = connection.cursor()

        cardnumber = current_cardnumber if 'current_cardnumber' in globals() else None

        cursor.execute(
            "INSERT INTO patients_l (cardnumber, registrationnumber, name, dateofbirth, age, gender, phonenumber) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                cardnumber,
                registrationnumber,
                name or None,
                dateofbirth or None,
                age ,
                gender or None,
                phonenumber or None
            )
        )
        connection.commit()
        cursor.close()
        connection.close()

        messagebox.showinfo("성공", "환자 정보가 등록되었습니다!")

        clear_fields()
        if 'current_cardnumber' in globals():
            del globals()['current_cardnumber']
    else:
        if cardnumber is None:
            messagebox.showwarning("등록 오류", "카드번호가 없습니다. 카드를 먼저 인식시켜 주세요.")
        return

#환자번호생성
def get_next_patient_number():
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(registrationnumber) FROM patients_l")
    result = cursor.fetchone()

    next_number = (int(result[0]) + 1) if result[0] is not None else 1
    cursor.close()
    connection.close()
    return f"{next_number:08d}"


#카드 인식
def read_from_arduino():
    global last_cardnumber, card_processing
    if not card_processing and arduino.in_waiting > 0:
        data_list = []
        while arduino.in_waiting > 0:
            data = arduino.readline().decode().strip()
            if data:
                data_list.append(data)
        for data in data_list:
            print(f"수신된 데이터: {data}")  # 디버깅용 출력
            if is_valid_cardnumber(data):
                    last_cardnumber = data
                    card_processing = True
                    card_detected(data)
    tk.after(100, read_from_arduino)


#환자등록번호조회(데이터베이스)
def search():
    patient_number = Ernumber.get()

    if patient_number:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM patients_l WHERE registrationnumber = ?", (patient_number,))
        result = cursor.fetchone()
        if result:
            display_patient_info(result) 
        else:
            messagebox.showwarning("조회 실패", "해당 번호의 환자가 없습니다.")
        cursor.close()
        connection.close()


#프로그램실행
def start():
    stbuton.destroy()
    setup_patient_info_screen()
    read_from_arduino()

#실행버튼
stbuton = Button(tk, text='프로그램실행', font=("Arial", 20), width=12, height=2, command=start)
stbuton.place(x=400, y=400)

tk.mainloop()

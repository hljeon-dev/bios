import tkinter as tk
from tkinter import messagebox
import random
from db import (
    save_total_weight,
    save_solo_weight,
    check_emotion_data_count,
    save_weekly_score,
    get_username,
    get_worker_by_category,
    save_matching_data, generate_report_json
)

# 선택한 감정, 세부 감정, 세부 상황을 저장하는 변수
selected_emotion = None
selected_detail_emotion = None
selected_detail = None
emotion_report = []  # 일주일간의 감정 데이터를 저장하는 리스트

MEMBER_ID = 2
WORKER_ID = 1

# 감정에 대한 가중치 설정
emotion_weights = {
    "매우좋음": 1,
    "좋음": 2,
    "약간좋음": 3,
    "모르겠음": 4,
    "약간나쁨": 5,
    "나쁨": 6,
    "매우나쁨": 7
}

# 세부 감정에 대한 가중치 설정
detail_emotion_weights = {
    "슬픔": 6,
    "분노": 5,
    "죄책감": 4,
    "두려움": 3,
    "수치심": 2,
    "혐오": 1
}

# 격려 및 위로 문구
encouragement_messages = [
    "오늘도 수고했어요! 계속 힘내세요!",
    "당신의 노력은 분명히 보상받을 거예요!",
    "오늘 하루도 멋진 하루였어요!"
]

neutral_messages = [
    "모든 날이 다 좋을 수는 없죠, 내일은 더 좋은 하루가 될 거예요.",
    "조금 헷갈리는 날일 수도 있지만, 잘 하고 있어요!",
    "오늘의 모호함이 내일의 명확함으로 바뀔 거예요."
]

# 감정 선택 함수
def select_emotion(emotion):
    global selected_emotion, detail_emotion_frame, detail_frame
    selected_emotion = emotion
    weight = emotion_weights[emotion]  # 감정 가중치 가져오기

    if emotion in ["매우좋음", "좋음", "약간좋음"]:
        message = random.choice(encouragement_messages)
        messagebox.showinfo("격려 메시지", f"{message}\n가중치: {weight}")
        selected_detail_emotion = None  # 세부 감정 선택하지 않음
        selected_detail = None  # 세부 상황 선택하지 않음

        # 데이터베이스에 단일 가중치 저장
        save_solo_weight(MEMBER_ID, weight, "해당 없음")

        save_emotion_report()  # 감정 데이터 저장
        reset_frames()  # 초기화 함수 호출
        show_frame(frame)  # 초기 화면으로 이동
    elif emotion == "모르겠음":
        message = random.choice(neutral_messages)
        messagebox.showinfo("위로 메시지", f"{message}\n가중치: {weight}")
        selected_detail_emotion = None  # 세부 감정 선택하지 않음
        selected_detail = None  # 세부 상황 선택하지 않음

        # 데이터베이스에 단일 가중치 저장
        save_solo_weight(MEMBER_ID, weight, "해당 없음")

        save_emotion_report()  # 감정 데이터 저장
        reset_frames()  # 초기화 함수 호출
        show_frame(frame)  # 초기 화면으로 이동
    elif emotion in ["매우나쁨", "나쁨", "약간나쁨"]:
        update_detail_emotions()
        show_frame(detail_emotion_frame)  # 세부 감정 선택으로 이동

# 세부 감정 선택 함수
def select_detail_emotion(detail_emotion):
    global selected_detail_emotion
    selected_detail_emotion = detail_emotion
    update_details(detail_emotion)
    show_frame(detail_frame)  # 세부 상황 선택으로 이동

# 세부 상황(키워드) 선택 함수
def select_detail(detail):
    global selected_detail
    selected_detail = detail
    emotion_weight = emotion_weights[selected_emotion]
    detail_weight = detail_emotion_weights.get(selected_detail_emotion, 0)
    total_weight = emotion_weight * detail_weight  # 감정 가중치와 세부 감정 가중치의 곱

    # 데이터베이스에 총 가중치 저장
    save_total_weight(MEMBER_ID, total_weight, selected_detail)

    messagebox.showinfo("정보", f"감정: {selected_emotion}\n세부 감정: {selected_detail_emotion}\n세부 상황: {selected_detail}\n총 가중치: {total_weight}")
    save_emotion_report()  # 감정 데이터 저장
    reset_frames()  # 초기화 함수 호출
    show_frame(frame)  # 선택 후 초기 화면으로 돌아가기

# 감정 데이터를 저장하는 함수
def save_emotion_report():
    global emotion_report
    report = {
        "emotion": selected_emotion,
        "detail_emotion": selected_detail_emotion,
        "detail": selected_detail
    }
    emotion_report.append(report)
    # 감정 기록이 7일치가 되면 관련 사회복지사에게 전송
    if len(emotion_report) == 7:
        send_report()

def match_with_social_worker(member_id, week_response_id, max_keyword):
    # max_keyword를 기준으로 사회복지사를 선택
    worker = get_worker_by_category(max_keyword)
    if worker:
        worker_id, worker_name = worker
        content = "상담 매칭 내용"

        # 매칭 데이터를 mw_matching 테이블에 저장
        save_matching_data(member_id, worker_id, week_response_id, max_keyword, content)

        # 상담 매칭 여부 확인
        prompt_counseling(worker_name)
    else:
        print(f"No social worker found for the keyword: {max_keyword}")

# 일주일 동안 데이터 수집
def send_report():
    # 데이터베이스에 주간 데이터를 저장하고 max_keyword 반환
    week_response_id, max_keyword = save_weekly_score(MEMBER_ID)

    # 매칭을 처리하는 함수 호출
    match_with_social_worker(MEMBER_ID, week_response_id, max_keyword)

    # 감정 보고서 초기화
    emotion_report.clear()

# 상담 매칭 여부 묻기 함수
def prompt_counseling(worker_name):
    username = get_username(MEMBER_ID)
    response = messagebox.askquestion("상담 매칭", f"{username}님과 관련된 사회복지사({worker_name})가 매칭되었습니다. 상담을 시작하시겠습니까?", icon='question')
    if response == 'yes':
        messagebox.showinfo("상담 매칭", "상담이 매칭되었습니다. 사회복지사가 곧 연락드릴 것입니다.")
    else:
        messagebox.showinfo("상담 매칭", "상담이 거부되었습니다. 필요시 다시 요청할 수 있습니다.")

# 감정에 따른 세부 감정 선택 프레임 업데이트 함수
def update_detail_emotions():
    for widget in detail_emotion_frame.winfo_children():
        widget.destroy()

    detail_emotions = ["분노", "혐오", "두려움", "죄책감", "슬픔", "수치심"]
    for i, detail_emotion in enumerate(detail_emotions):
        detail_emotion_button = tk.Button(detail_emotion_frame, text=detail_emotion, font=("Arial", 18), command=lambda d=detail_emotion: select_detail_emotion(d))
        detail_emotion_button.grid(row=1, column=i, padx=20, pady=20)

    for i in range(6):
        detail_emotion_frame.grid_columnconfigure(i, weight=1)
    detail_emotion_frame.grid_rowconfigure(1, weight=1)

# 세부 감정에 따른 세부 상황(키워드) 선택 프레임 업데이트 함수
def update_details(detail_emotion):
    for widget in detail_frame.winfo_children():
        widget.destroy()

    details = ['학업', '대인관계', '가정 문제', '진로 문제', '정체성 및 자아 탐색', '기타']
    for i, detail in enumerate(details):
        detail_button = tk.Button(detail_frame, text=detail, font=("Arial", 18), command=lambda d=detail: select_detail(d))
        detail_button.grid(row=1, column=i, padx=20, pady=20)

    for i in range(6):
        detail_frame.grid_columnconfigure(i, weight=1)
    detail_frame.grid_rowconfigure(1, weight=1)

# 페이지 프레임 전환 함수
def show_frame(frame):
    frame.tkraise()

# 프레임 초기화 함수
def reset_frames():
    for widget in detail_emotion_frame.winfo_children():
        widget.destroy()
    for widget in detail_frame.winfo_children():
        widget.destroy()
    detail_emotion_frame.lower()
    detail_frame.lower()

# 프로그램 시작 시 자동으로 주간 데이터를 저장하는 함수
def check_and_save_weekly_data():
    member_id = MEMBER_ID  # 사용자의 ID

    if check_emotion_data_count(member_id):  # 감정 데이터가 7개 이상인지 확인
        save_weekly_score(member_id)  # 주간 데이터 저장
        username = get_username(member_id)  # 사용자 이름 가져오기
        messagebox.showinfo("정보", f"{username}님의 주간 감정 데이터를 관련된 사회복지사에게 전송하였습니다.")
        generate_report_json(member_id)

# GUI 창 초기화
root = tk.Tk()
root.title("청소년 감정 기록 시스템")
root.geometry("1080x1920")  # 창 크기를 1080x1920 해상도로 설정

# 프로그램 시작 시 자동으로 주간 데이터를 확인 및 저장
check_and_save_weekly_data()

# 상단 라벨 고정
label = tk.Label(root, text="오늘의 감정을 선택하세요:", font=("Arial", 24))
label.pack(side="top", pady=30)

# 감정 선택 프레임
frame = tk.Frame(root)
frame.pack(pady=30)

# 감정 선택 버튼 생성
emotions = ["매우좋음", "좋음", "약간좋음", "모르겠음", "매우나쁨", "나쁨", "약간나쁨"]
for i, emotion in enumerate(emotions):
    button = tk.Button(frame, text=emotion, font=("Arial", 24), width=12, height=2, command=lambda e=emotion: select_emotion(e))
    button.grid(row=0, column=i, padx=20, pady=20)

for i in range(7):
    frame.grid_columnconfigure(i, weight=1)

# 세부 감정 선택 프레임
detail_emotion_frame = tk.Frame(root)
detail_emotion_frame.place(relwidth=1, relheight=1)

# 세부 상황(키워드) 선택 프레임
detail_frame = tk.Frame(root)
detail_frame.place(relwidth=1, relheight=1)

# 첫 번째 페이지를 기본으로 표시
show_frame(frame)

# GUI 메인 루프 실행
root.mainloop()

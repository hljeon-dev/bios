from tkinter import messagebox

from db import save_emotion_data, get_weekly_score, get_max_keyword, save_solo_weight

# 감정 점수 단일 계산 함수
def process_solo_emotion_data(emotion, detail):
    emotion_score = calculate_score(emotion)

    member_id = 2
    t = save_solo_weight(member_id, emotion, emotion_score)

    return t


def calculate_score(emotion):
    emotion_points = {
        "매우좋음": 1,
        "좋음": 2,
        "약간좋음": 3,
        "모르겠음": 4,
        "약간나쁨": 5,
        "나쁨": 6,
        "매우나쁨": 7
    }
    score = emotion_points.get(emotion)

    return score

# 감정 점수 계산 및 데이터 처리 함수
def process_emotion_data(emotion, detail_emotion, detail):
    # 감정 점수 계산 로직 (예: 감정에 따라 점수를 다르게 설정)
    emotion_score = calculate_emotion_score(emotion, detail_emotion)

    # 데이터베이스에 감정 데이터 저장
    member_id = 2  # 예시로 사용자의 ID를 2로 가정
    save_emotion_data(member_id, emotion, detail_emotion, detail, emotion_score)

    # 주간 점수 계산
    weekly_score = get_weekly_score(member_id)

    # 최고 카운팅 키워드 조회
    max_keyword = get_max_keyword(member_id)

    # 기준치를 넘었는지 확인
    if weekly_score >= 210:
        report_to_social_worker(member_id, weekly_score, max_keyword)


# 감정 점수 계산 함수
def calculate_emotion_score(emotion, detail_emotion):
    # 감정과 세부 감정에 따라 점수를 계산
    emotion_points = {
        "매우좋음": 1,
        "좋음": 2,
        "약간좋음": 3,
        "모르겠음": 4,
        "약간나쁨": 5,
        "나쁨": 6,
        "매우나쁨": 7
    }
    detail_points = {
        "슬픔": 6,
        "분노": 5,
        "죄책감": 4,
        "두려움": 3,
        "수치심": 2,
        "혐오": 1
    }

    score = emotion_points.get(emotion, 0) * detail_points.get(detail_emotion, 1)
    return score

# 사회복지사에게 보고서 전송 및 사용자 알림 함수
def report_to_social_worker(member_id, weekly_score, max_keyword):
    # 사회복지사에게 보고서 전송 로직
    social_worker_name = "아무개"  # 예시로 사회복지사의 이름을 사용
    print(f"보고서: 사용자 {member_id}의 주간 점수가 {weekly_score}점으로 {social_worker_name} 사회복지사와 상담이 필요합니다.")

    # 사용자에게 알림 전송
    messagebox.showinfo("알림", f"{social_worker_name} 사회복지사와 상담이 연결됩니다.")

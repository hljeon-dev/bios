import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

import mysql.connector

# .env 파일에서 환경 변수 로드
load_dotenv()

# MySQL 연결 설정
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# 총 가중치와 키워드를 데이터베이스에 저장하는 함수
def save_total_weight(member_id, score, keyword):
    connection = get_db_connection()
    cursor = connection.cursor()

    sql = """
    INSERT INTO Emotions (member_id, datetime, score, keyword)
    VALUES (%s, NOW(), %s, %s)
    """
    val = (member_id, score, keyword)

    cursor.execute(sql, val)
    connection.commit()

    print(cursor.rowcount, "record inserted.")

    cursor.close()
    connection.close()

# 단일 가중치와 세부 정보를 데이터베이스에 저장하는 함수
def save_solo_weight(member_id, score, keyword):
    connection = get_db_connection()
    cursor = connection.cursor()

    sql = """
    INSERT INTO Emotions (member_id, datetime, score, keyword)
    VALUES (%s, NOW(), %s, %s)
    """
    val = (member_id, score, keyword)

    cursor.execute(sql, val)
    connection.commit()

    print(cursor.rowcount, "record inserted.")

    cursor.close()
    connection.close()

# 감정 데이터를 데이터베이스에 저장하는 함수
def save_emotion_data(member_id, detail, score):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    sql = """
    INSERT INTO Emotions (member_id, datetime, score, keyword)
    VALUES (%s, NOW(), %d, %s)
    """
    cursor.execute(sql, (member_id, score, detail))
    db_connection.commit()
    cursor.close()
    db_connection.close()

# 주간 감정 데이터를 계산하는 함수
def get_weekly_score(user_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    sql = """
    SELECT SUM(score) FROM Emotions
    WHERE user_id = %s AND datetime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    """
    cursor.execute(sql, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    db_connection.close()
    return result[0] if result else 0

# 최고 카운팅 키워드 조회 함수
def get_max_keyword(user_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    sql = """
    SELECT keyword, COUNT(*) as cnt FROM Emotions
    WHERE user_id = %s AND datetime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    GROUP BY keyword
    ORDER BY cnt DESC
    LIMIT 1
    """
    cursor.execute(sql, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    db_connection.close()
    return result[0] if result else None

# 사용자의 감정 데이터가 7개 이상인지 확인하는 함수
def check_emotion_data_count(member_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    sql = """
    SELECT COUNT(*) FROM Emotions
    WHERE member_id = %s
    """
    cursor.execute(sql, (member_id,))
    count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return count >= 7  # 7개 이상인 경우 True 반환

# 일주일 동안의 가중치를 합산하고 week_responses 테이블에 저장하는 함수
def save_weekly_score(member_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # 현재 날짜와 일주일 전 날짜 계산
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)

    # 일주일 동안의 가중치 합산
    sql = """
    SELECT SUM(score) FROM Emotions
    WHERE member_id = %s AND datetime BETWEEN %s AND %s
    """
    cursor.execute(sql, (member_id, one_week_ago, today))
    total_score = cursor.fetchone()[0] or 0

    # 일주일 동안 가장 많이 사용된 키워드 찾기
    sql_keyword = """
    SELECT keyword, COUNT(keyword) as cnt FROM Emotions
    WHERE member_id = %s AND datetime BETWEEN %s AND %s
    GROUP BY keyword
    ORDER BY cnt DESC
    LIMIT 1
    """
    cursor.execute(sql_keyword, (member_id, one_week_ago, today))
    max_keyword_result = cursor.fetchone()
    max_keyword = max_keyword_result[0] if max_keyword_result else "N/A"

    # 결과를 week_responses 테이블에 저장
    sql_insert = """
    INSERT INTO week_responses (member_id, week_score, max_keyword)
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql_insert, (member_id, total_score, max_keyword))
    connection.commit()

    print(cursor.rowcount, "weekly score inserted.")

    cursor.close()
    connection.close()

    # 사용자 이름을 가져오는 함수
def get_username(member_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "SELECT username FROM members WHERE member_id = %s"
    cursor.execute(sql, (member_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return result[0]
    return None

# 주간 감정 데이터를 가져오는 함수
def get_weekly_emotion_data(member_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """
    SELECT score, keyword 
    FROM emotions 
    WHERE member_id = %s 
    ORDER BY datetime DESC 
    LIMIT 7
    """
    cursor.execute(sql, (member_id,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

# 주간 데이터를 저장하는 함수
def save_weekly_score(member_id):
    # 일주일 동안의 감정 데이터를 가져옴
    data = get_weekly_emotion_data(member_id)

    if not data:
        return

    # 점수 합산 및 키워드 계산
    total_score = sum([row[0] for row in data])
    keywords = [row[1] for row in data]
    max_keyword = max(set(keywords), key=keywords.count)

    # 주간 데이터를 week_responses 테이블에 저장
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """
    INSERT INTO week_responses (member_id, week_score, max_keyword) 
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (member_id, total_score, max_keyword))
    connection.commit()
    cursor.close()
    connection.close()

# 주간 데이터와 멤버 - 사회복지사간 매칭하는 함수
def save_matching_data(member_id, worker_id, week_response_id, max_keyword, content):
    connection = get_db_connection()
    cursor = connection.cursor()

    # 먼저 주간 데이터의 max_keyword가 social_workers 테이블의 category와 일치하는지 확인
    cursor.execute("""
        SELECT worker_id FROM social_workers
        WHERE worker_id = %s AND category = %s
    """, (worker_id, max_keyword))

    result = cursor.fetchone()

    if result:
        # 일치하는 경우에만 매칭 데이터를 mw_matching 테이블에 저장
        sql = """
        INSERT INTO mw_matching (member_id, worker_id, week_response_id, max_keyword, content)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (member_id, worker_id, week_response_id, max_keyword, content))
        connection.commit()
        print("매칭 성공: 데이터가 mw_matching 테이블에 저장되었습니다.")
    else:
        print("매칭 실패: max_keyword와 사회복지사 카테고리가 일치하지 않습니다.")

    cursor.close()
    connection.close()


def get_worker_by_category(max_keyword):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "SELECT worker_id, username FROM social_workers WHERE category = %s LIMIT 1"
    cursor.execute(sql, (max_keyword,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

# 주간 보고서 저장
def generate_report_json(member_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # 주간 응답 데이터를 조회
    sql = """
    SELECT week_score, max_keyword 
    FROM week_responses 
    WHERE member_id = %s
    ORDER BY week_response_id DESC LIMIT 1
    """
    cursor.execute(sql, (member_id,))
    result = cursor.fetchone()

    if result:
        week_score, max_keyword = result
        username = get_username(member_id)

        # 상담사의 이름을 social_workers 테이블에서 조회
        worker_sql = """
        SELECT username 
        FROM social_workers 
        WHERE category = %s
        LIMIT 1
        """
        cursor.execute(worker_sql, (max_keyword,))
        worker_result = cursor.fetchone()

        if worker_result:
            worker_name = worker_result[0]

            # 보고서 내용 생성
            report_data = {
                "username": username,
                "week_score": week_score,
                "max_keyword": max_keyword,
                "worker_name": worker_name,
                "recommendation": "위 두 항목을 근거로 상담이 필요함."
            }

            # reports 폴더가 없으면 생성
            os.makedirs("reports", exist_ok=True)

            # 파일 이름을 설정 (예: reports/username_report.json)
            file_name = f"reports/{username}_report.json"

            # JSON 파일로 보고서를 저장
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(report_data, file, ensure_ascii=False, indent=4)

            print(f"보고서가 {file_name}로 JSON 형식으로 저장되었습니다.")
        else:
            print("해당 키워드에 맞는 상담사가 존재하지 않습니다. 보고서를 생성하지 않습니다.")
    else:
        print("해당 사용자의 주간 보고서를 찾을 수 없습니다.")

    cursor.close()
    connection.close()

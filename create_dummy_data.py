import sqlite3
from datetime import datetime, timedelta
import random

# 데이터베이스 연결하기
def create_connection():
    """
    SQLite 데이터베이스에 연결하는 함수야
    """
    try:
        conn = sqlite3.connect('trading_history.db')
        return conn
    except sqlite3.Error as e:
        print(f"데이터베이스 연결 중 에러가 났어!: {e}")
        return None

# 테이블 만들기
def create_table(conn):
    """
    거래 기록을 저장할 테이블을 만드는 함수야
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                decision TEXT NOT NULL,
                percentage INTEGER NOT NULL,
                reason TEXT NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"테이블 만들기 중 에러가 났어!: {e}")

# 더미 데이터 만들기
def generate_dummy_data():
    """
    4일치의 거래 기록 더미 데이터를 만드는 함수야
    하루에 5개씩, 총 20개의 기록을 만들어
    """
    conn = create_connection()
    if conn is None:
        return

    create_table(conn)
    cursor = conn.cursor()

    # 먼저 기존 데이터를 모두 지워줄게
    cursor.execute("DELETE FROM trading_history")
    
    decisions = ['BUY', 'SELL', 'HOLD']
    reasons = [
        "비트코인 가격이 지지선에 도달했어!",
        "거래량이 급증하고 있어서 좋은 신호야!",
        "시장이 불안정해 보여서 잠시 기다리는게 좋을 것 같아!",
        "상승 추세가 확실해 보여!",
        "하락 신호가 보여서 조심해야해!"
    ]

    # 현재 시간부터 3일 전까지의 데이터를 만들거야
    current_time = datetime.now()
    
    for days_ago in range(4):  # 0부터 3까지 (오늘, 어제, 그제, 3일전)
        base_date = current_time - timedelta(days=days_ago)
        
        # 하루에 5번의 거래 기록을 만들어볼게
        for i in range(5):
            # 시간은 9시부터 18시 사이로 랜덤하게 정할게
            hour = random.randint(9, 18)
            minute = random.randint(0, 59)
            timestamp = base_date.replace(hour=hour, minute=minute)
            
            decision = random.choice(decisions)
            percentage = random.randint(60, 95)  # 60%에서 95% 사이의 확률
            reason = random.choice(reasons)
            
            # 데이터베이스에 저장하기
            cursor.execute('''
                INSERT INTO trading_history (timestamp, decision, percentage, reason)
                VALUES (?, ?, ?, ?)
            ''', (timestamp.strftime('%Y-%m-%d %H:%M:%S'), decision, percentage, reason))

    # 변경사항 저장하기
    conn.commit()
    conn.close()
    print("더미 데이터 생성이 완료됐어!")

if __name__ == "__main__":
    generate_dummy_data() 
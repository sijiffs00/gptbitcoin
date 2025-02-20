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
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                img TEXT,
                price REAL,
                decision TEXT,
                percentage INTEGER,
                reason TEXT,
                original_reason TEXT
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"테이블 만들기 중 에러가 났어!: {e}")

# 더미 데이터 만들기
def generate_dummy_data():
    """
    4일치의 거래 기록 더미데이터를 만드는 함수야
    하루에 5개씩, 총 20개의 기록을 만들어
    """
    conn = create_connection()
    if conn is None:
        return

    create_table(conn)
    cursor = conn.cursor()

    # 먼저 기존 데이터를 모두 지워줄게
    cursor.execute("DELETE FROM trades")
    
    decisions = ['BUY', 'SELL', 'HOLD']
    
    # S3 이미지 URL 패턴
    image_url_base = "https://aibitcoin-chart-img.s3.ap-northeast-2.amazonaws.com/bitcoin_charts/"
    
    # 한국어 이유와 영어 이유 쌍
    reasons = [
        (
            "RSI가 과매수 구간에 진입했고, 가격이 상단 볼린저 밴드에 근접해 있어. 단기 조정이 예상돼!",
            "RSI has entered overbought territory and price is approaching the upper Bollinger Band, suggesting a potential short-term correction."
        ),
        (
            "거래량이 급증하고 있고, MACD가 강한 상승 신호를 보여주고 있어!",
            "Trading volume is surging and MACD shows strong bullish signals."
        ),
        (
            "시장이 불안정해 보이고 변동성이 높아서 잠시 관망하는게 좋을 것 같아!",
            "Market appears unstable with high volatility, suggesting a wait-and-see approach."
        ),
        (
            "가격이 주요 지지선에서 반등하고 있고, RSI도 과매도 구간에서 회복 중이야!",
            "Price is bouncing from key support level and RSI is recovering from oversold conditions."
        ),
        (
            "단기 이동평균선이 장기 이동평균선을 하향 돌파했어. 약세 신호가 나타나고 있어!",
            "Short-term moving average has crossed below the long-term moving average, indicating bearish signals."
        )
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
            
            # 이미지 URL 생성 (실제 날짜 형식에 맞춰서)
            img_url = f"{image_url_base}{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
            
            decision = random.choice(decisions)
            percentage = random.randint(60, 95)  # 60%에서 95% 사이의 확률
            price = random.uniform(50000, 55000)  # 비트코인 가격 범위
            reason_pair = random.choice(reasons)
            
            # 데이터베이스에 저장하기
            cursor.execute('''
                INSERT INTO trades (
                    timestamp,
                    img,
                    price,
                    decision,
                    percentage,
                    reason,
                    original_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                img_url,
                price,
                decision,
                percentage,
                reason_pair[0],  # 한국어 이유
                reason_pair[1]   # 영어 이유
            ))

    # 변경사항 저장하기
    conn.commit()
    conn.close()
    print("더미 데이터 생성이 완료됐어!")

if __name__ == "__main__":
    generate_dummy_data() 
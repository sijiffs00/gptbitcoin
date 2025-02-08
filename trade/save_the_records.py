import sqlite3  # SQLite 데이터베이스를 사용하기 위한 모듈이야
from datetime import datetime  # 현재 시간을 기록하기 위한 모듈이야
import pytz  # 시간대 처리를 위한 라이브러리야

def save_the_record(price, decision, percentage, reason, img_url=None):
    """
    매매 기록을 데이터베이스에 저장하는 함수야
    price: 비트코인의 현재 가격
    decision: AI가 결정한 거래 종류 (buy/sell/hold)
    percentage: AI가 제안한 거래 비율
    reason: AI가 결정한 이유
    img_url: S3에 저장된 차트 이미지 URL
    """
    try:
        # 한국 시간대 설정하기
        kst = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

        # 데이터베이스에 연결하기
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()

        # 기존 테이블이 있는지 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
        table_exists = cursor.fetchone() is not None

        if table_exists:
            # img 칼럼이 있는지 확인
            cursor.execute("PRAGMA table_info(trades)")
            columns = cursor.fetchall()
            has_img_column = any(col[1] == 'img' for col in columns)

            # img 칼럼이 없다면 추가
            if not has_img_column:
                cursor.execute("ALTER TABLE trades ADD COLUMN img TEXT")
                print("✨ 'img' 칼럼이 성공적으로 추가되었어!")
        else:
            # 새로운 테이블 생성
            cursor.execute('''
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                img TEXT,           -- S3 이미지 URL을 저장할 새로운 칼럼
                price REAL,
                decision TEXT,
                percentage INTEGER,
                reason TEXT
            )
            ''')

        # 새로운 거래 기록 저장하기 (이제 img_url도 포함)
        cursor.execute('''
        INSERT INTO trades (timestamp, img, price, decision, percentage, reason)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_time, img_url, price, decision, percentage, reason))

        # 변경사항 저장하기
        conn.commit()
        print("✅ 거래 기록이 성공적으로 저장되었어!")

    except sqlite3.Error as e:
        # 에러가 발생하면 어떤 에러인지 알려주기
        print(f"❌ 데이터베이스 에러가 발생했어: {e}")

    finally:
        # 데이터베이스 연결 닫기 (이건 꼭 해야해!)
        if conn:
            conn.close()
            print("🔒 데이터베이스 연결을 안전하게 닫았어!")

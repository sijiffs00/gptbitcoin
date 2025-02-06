import sqlite3  # SQLite 데이터베이스를 사용하기 위한 모듈이야
from datetime import datetime  # 현재 시간을 기록하기 위한 모듈이야

def save_the_record(price, decision, percentage, reason):
    """
    매매 기록을 데이터베이스에 저장하는 함수야
    price: 비트코인의 현재 가격
    decision: AI가 결정한 거래 종류 (buy/sell/hold)
    percentage: AI가 제안한 거래 비율
    reason: AI가 결정한 이유
    """
    try:
        # 데이터베이스에 연결하기
        conn = sqlite3.connect('trading_history.db')  # trading_history.db 파일에 연결해
        cursor = conn.cursor()  # 데이터베이스에 명령을 내리기 위한 커서를 만들어

        # trades 테이블이 없다면 새로 만들기
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 자동으로 증가하는 고유번호
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 거래 시간
            price REAL,      -- 비트코인 현재가격
            decision TEXT,   -- AI의 결정 (buy/sell/hold)
            percentage INTEGER,  -- AI가 제안한 거래 비율
            reason TEXT      -- AI의 판단 이유
        )
        ''')

        # 새로운 거래 기록 저장하기
        cursor.execute('''
        INSERT INTO trades (price, decision, percentage, reason)
        VALUES (?, ?, ?, ?)
        ''', (price, decision, percentage, reason))

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

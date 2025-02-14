import sqlite3  # SQLite 데이터베이스를 사용하기 위한 모듈이야
from datetime import datetime  # 현재 시간을 기록하기 위한 모듈이야
import pytz  # 시간대 처리를 위한 라이브러리야
import os
from openai import OpenAI

def translate_with_gpt(text):
    """
    영어로 된 트레이딩 분석을 한국어로 번역하고 요약하는 함수
    """
    try:
        # OpenAI API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OpenAI API 키가 설정되지 않았어요!")
            return text

        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 트레이딩 전문 번역가야. 영어로 된 트레이딩 분석 내용을 한국어로 번역해. 반말을 사용해야해. 중학생이 이해할수있는 수준으로 쉽게 풀어서 요약해줘. 3줄로 요약해야 해."},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        
        translated_text = response.choices[0].message.content
        print(f"✅ 번역 완료: {translated_text}")
        return translated_text

    except Exception as e:
        print(f"❌ GPT 번역 중 오류 발생: {str(e)}")
        print(f"원본 텍스트로 진행합니다: {text}")
        return text

def save_the_record(price, decision, percentage, reason, img_url=None):
    """
    매매 기록을 데이터베이스에 저장하는 함수야
    price: 비트코인의 현재 가격
    decision: AI가 결정한 거래 종류 (buy/sell/hold)
    percentage: AI가 제안한 거래 비율
    reason: AI가 결정한 이유 (영어)
    img_url: S3에 저장된 차트 이미지 URL
    
    Returns:
        str: 한국어로 번역된 reason
    """
    try:
        # 먼저 reason을 한국어로 번역
        korean_reason = translate_with_gpt(reason)

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
            # 필요한 칼럼들이 있는지 확인
            cursor.execute("PRAGMA table_info(trades)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # 필요한 칼럼들 추가
            if 'img' not in column_names:
                cursor.execute("ALTER TABLE trades ADD COLUMN img TEXT")
                print("✨ 'img' 칼럼이 성공적으로 추가되었어!")
            if 'original_reason' not in column_names:
                cursor.execute("ALTER TABLE trades ADD COLUMN original_reason TEXT")
                print("✨ 'original_reason' 칼럼이 성공적으로 추가되었어!")
        else:
            # 새로운 테이블 생성 (이제 original_reason 칼럼도 포함)
            cursor.execute('''
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                img TEXT,           -- S3 이미지 URL을 저장할 칼럼
                price REAL,
                decision TEXT,
                percentage INTEGER,
                reason TEXT,        -- 한국어로 번역된 이유
                original_reason TEXT -- 원본 영어 이유
            )
            ''')

        # 새로운 거래 기록 저장하기 (번역된 reason과 원본 reason 모두 저장)
        cursor.execute('''
        INSERT INTO trades (timestamp, img, price, decision, percentage, reason, original_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (current_time, img_url, price, decision, percentage, korean_reason, reason))

        # 변경사항 저장하기
        conn.commit()
        print("✅ 거래 기록이 성공적으로 저장되었어!")
        
        return korean_reason  # 번역된 텍스트 반환

    except sqlite3.Error as e:
        # 에러가 발생하면 어떤 에러인지 알려주기
        print(f"❌ 데이터베이스 에러가 발생했어: {e}")
        return reason  # 에러 발생시 원본 텍스트 반환

    finally:
        # 데이터베이스 연결 닫기 (이건 꼭 해야해!)
        if conn:
            conn.close()
            print("🔒 데이터베이스 연결을 안전하게 닫았어!")

import sqlite3  # SQLite 데이터베이스를 사용하기 위한 모듈이야
from datetime import datetime  # 현재 시간을 기록하기 위한 모듈이야
import pytz  # 시간대 처리를 위한 라이브러리야
import os
from openai import OpenAI
import time
import requests
import json

def translate_with_deepseek(text):
    """
    영어로 된 트레이딩 분석을 DeepSeek 모델을 사용해 한국어로 번역하고 요약하는 함수
    """
    try:
        # DeepSeek API 키 확인
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ DeepSeek API 키가 설정되지 않았어요!")
            # API 키가 없으면 간단한 번역으로 대체
            return f"[번역 실패] {text[:150]}... (API 키 없음)"

        # DeepSeek API 엔드포인트
        url = "https://api.deepseek.com/v1/chat/completions"
        
        # 요청 헤더 설정
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # API 요청 최대 3번 시도
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 요청 데이터 설정
                data = {
                    "model": "deepseek-chat",  # DeepSeek V3 모델 사용
                    "messages": [
                        {
                            "role": "system", 
                            "content": "너는 트레이딩 전문 번역가야. 영어로 된 트레이딩 분석 내용을 한국어로 번역해. 반말을 사용해. 중학생이 이해할수있는 수준으로 쉽게 요약해줘. 3줄로 요약해."
                        },
                        {
                            "role": "user", 
                            "content": text
                        }
                    ],
                    "temperature": 0.5,  # 더 결정적인 응답을 위해 온도 낮춤
                    "max_tokens": 200  # 토큰 수 줄임
                }
                
                # API 요청 보내기
                response = requests.post(url, headers=headers, json=data, timeout=30)  # 타임아웃 30초로 증가
                
                # 응답 상태 확인
                if response.status_code == 200:
                    result = response.json()
                    translated_text = result["choices"][0]["message"]["content"]
                    
                    # 토큰 사용량 출력 (있을 경우)
                    if "usage" in result:
                        print("\n🎯 DeepSeek 토큰 사용량:")
                        print(f"입력 토큰: {result['usage']['prompt_tokens']}개")
                        print(f"출력 토큰: {result['usage']['completion_tokens']}개")
                        print(f"총 토큰: {result['usage']['total_tokens']}개")
                    
                    print(f"✅ DeepSeek 번역 완료: {translated_text}")
                    return translated_text
                else:
                    print(f"❌ DeepSeek API 요청 실패: 상태 코드 {response.status_code}")
                    print(response.text)
                    if attempt == max_retries - 1:  # 마지막 시도였으면
                        raise Exception(f"API 요청 실패: {response.text}")
                    time.sleep(1)  # 1초 대기 후 재시도
            except Exception as retry_error:
                print(f"❌ DeepSeek 번역 시도 {attempt+1}/{max_retries} 실패: {str(retry_error)}")
                if attempt == max_retries - 1:  # 마지막 시도였으면
                    raise  # 예외를 다시 발생시켜 아래 except 블록으로 이동
                time.sleep(1)  # 1초 대기 후 재시도
                
    except Exception as e:
        print(f"❌ DeepSeek 번역 중 오류 발생: {str(e)}")
        print(f"원본 텍스트로 진행합니다: {text}")
        
        # 번역 실패 시 간단한 메시지로 대체
        if text and len(text) > 10:  # 텍스트가 있고 충분히 길면
            # 간단한 메시지로 대체 (현지화)
            if "buy" in text.lower():
                return "비트코인 매수 신호가 감지됐어! 기술적 지표와 시장 분위기가 긍정적이야. 거래량도 좋고 상승 추세가 유지되고 있어."
            elif "sell" in text.lower():
                return "비트코인 매도 신호야! 기술적 지표가 하락세를 보이고 있어. 위험 신호가 보이니 수익 실현을 고려해봐."
            elif "hold" in text.lower():
                return "지금은 관망하는 게 좋을 것 같아. 시장이 혼란스럽고 명확한 방향이 안 보여. 더 확실한 신호가 올 때까지 기다려봐."
            else:
                return f"[번역 실패] 영어 원문: {text[:150]}..."  # 원문 앞부분만 표시
        else:
            return f"[번역 실패] 영어 원문: {text}"

def save_the_record(price, decision, reason):
    """
    매매 기록을 데이터베이스에 저장하는 함수야
    price: 비트코인의 현재 가격
    decision: AI가 결정한 거래 종류 (buy/sell/hold)
    reason: AI가 결정한 이유 (영어)
    
    Returns:
        str: 한국어로 번역된 reason
    """
    try:
        # 먼저 reason을 한국어로 번역 (DeepSeek 사용)
        korean_reason = translate_with_deepseek(reason)

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
            if 'original_reason' not in column_names:
                cursor.execute("ALTER TABLE trades ADD COLUMN original_reason TEXT")
                print("✨ 'original_reason' 칼럼이 성공적으로 추가되었어!")
            if 'lookback' not in column_names:
                cursor.execute("ALTER TABLE trades ADD COLUMN lookback TEXT")
                print("✨ 'lookback' 칼럼이 성공적으로 추가되었어!")
        else:
            # 새로운 테이블 생성
            cursor.execute('''
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                price REAL,
                decision TEXT,
                reason TEXT,        -- 한국어로 번역된 이유
                original_reason TEXT, -- 원본 영어 이유
                lookback TEXT       -- 거래 결과 회고
            )
            ''')

        # 새로운 거래 기록 저장하기 (lookback은 NULL로 저장)
        cursor.execute('''
        INSERT INTO trades (timestamp, price, decision, reason, original_reason, lookback)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_time, price, decision, korean_reason, reason, None))

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

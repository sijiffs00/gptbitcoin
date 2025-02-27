import os
from dotenv import load_dotenv
import threading
import time
import sqlite3
from flask_api_server import run_server
from trade.ai_trading import ai_trading
import json
from openai import OpenAI

# 0. env 파일 로드
load_dotenv()

def get_gpt_analysis(prompt):
    """GPT에게 분석을 요청하는 함수"""
    client = OpenAI()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert Bitcoin trading analyst. Analyze the trading history and current investment status, then provide evaluation and advice.

You MUST respond in this exact JSON format:
{
    "return_rate": "current return rate as a number",
    "lookback": "detailed analysis and advice including all 4 requested points"
}"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0.7,
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        print("\n🎯 토큰 사용량:")
        print(f"프롬프트 토큰: {response.usage.prompt_tokens}개")
        print(f"응답 토큰: {response.usage.completion_tokens}개")
        print(f"전체 토큰: {response.usage.total_tokens}개")
        
        return json.loads(result)
        
    except Exception as e:
        print(f"❌ GPT API 호출 중 에러 발생: {str(e)}")
        return None

def remind_records():
    try:
        # SQLite DB 연결
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()
        
        # 거래 기록 확인
        cursor.execute("SELECT COUNT(*) FROM trades")
        record_count = cursor.fetchone()[0]
        
        if record_count == 0:
            print("⚠️ 아직 매매기록이 없습니다.")
            return
            
        print('매매기록 재귀개선 로직실행')
        
        # 모든 거래 기록 가져오기
        cursor.execute("""
            SELECT 
                timestamp as trade_time,
                decision,
                price,
                reason,
                lookback
            FROM trades
            ORDER BY timestamp DESC
        """)
        
        trades = cursor.fetchall()
        
        # GPT에게 제공할 매매 분석 프롬프트 작성
        analysis_prompt = """
=== 비트코인 트레이딩 기록 분석 요청 ===

[전체 거래 요약]
총 거래 수: {total_trades}개
매수 거래: {buy_trades}개
매도 거래: {sell_trades}개
홀딩 결정: {hold_trades}개

[상세 거래 기록]
{detailed_trades}

위 매매기록을 바탕으로 조언해줘.

1. 현재 트레이딩 전략의 장단점
2. 개선이 필요한 부분
3. 앞으로의 거래를 위한 구체적인 전략 조언

이 3가지 항목이 포함된 트레이딩 조언을 해줘. 200자 이내로 작성하고 친구에게 말하는 것처럼 쉽게 친숙한 어휘를 사용해야해.

""".strip()

        # 거래 통계 계산
        buy_trades = sum(1 for trade in trades if trade[1] == 'buy')
        sell_trades = sum(1 for trade in trades if trade[1] == 'sell')
        hold_trades = sum(1 for trade in trades if trade[1] == 'hold')
        
        # 상세 거래 기록 포맷팅
        detailed_trades = ""
        for i, (time, decision, price, reason, lookback) in enumerate(trades, 1):
            detailed_trades += f"""
거래 #{i}
시간: {time}
결정: {decision}
가격: {price:,} KRW
---""".strip() + "\n\n"
        
        # 최종 프롬프트 생성
        final_prompt = analysis_prompt.format(
            total_trades=record_count,
            buy_trades=buy_trades,
            sell_trades=sell_trades,
            hold_trades=hold_trades,
            detailed_trades=detailed_trades
        )
        
        print("\n=== GPT 분석용 트레이딩 기록 ===")
        print(final_prompt)
        
        # GPT API 호출
        analysis_result = get_gpt_analysis(final_prompt)
        if analysis_result:
            print("\n=== GPT 분석 결과 ===")
            print(f"분석 및 조언:\n{analysis_result['lookback']}")
        
    except sqlite3.OperationalError as e:
        if 'no such table' in str(e):
            print("⚠️ 아직 거래 기록 데이터베이스가 없습니다.")
            return
        raise e
    except Exception as e:
        print(f"❌ 데이터베이스 조회 중 에러 발생: {str(e)}")
        return
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    # API 서버를 별도의 스레드로 실행
    api_thread = threading.Thread(target=run_server)
    api_thread.daemon = True  # 메인 프로그램이 종료되면 API 서버도 종료
    api_thread.start()
    print("🚀 API 서버가 시작되었습니다 (포트: 8000)")
    
    print("🤖 트레이딩 봇이 시작됩니다...")
    while True:
        try:
            remind_records() 
            ai_trading()
            print("\n⏰ 1시간 후에 다음 분석을 시작합니다...")
            time.sleep(3600)  # 1시간(3600초) 대기
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다...")
            break
        except Exception as e:
            print(f"\n❌ 에러 발생: {str(e)}")
            print("⏰ 10초 후에 다시 시작합니다...")
            time.sleep(10)



import sqlite3
import json
from openai import OpenAI
import os

def remind_records():
    try:
        print("remind_records 실행")

        # 1. 로컬db의 'trades' 테이블에서 매매기록 모두 가져오기
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC")
        trades = cursor.fetchall()
        
        if not trades:
            print("매매기록이 없습니다.")
            return

        # 매매기록을 보기 좋게 정리
        trade_records = []
        for trade in trades:
            trade_dict = {
                "timestamp": trade[1],
                "decision": trade[4],  # img가 아닌 decision 컬럼을 가져와야 함
                "price": trade[3]
            }
            trade_records.append(trade_dict)

        # 2. GPT-4에게 매매기록 분석 요청
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""당신은 비트코인 트레이딩 전문가입니다.
        다음 비트코인 매매 기록을 분석하여 투자 현황과 앞으로의 전략을 조언해주세요.
        
        매매기록:
        {json.dumps(trade_records, indent=2, ensure_ascii=False)}
        
        반드시 다음과 같은 JSON 형식으로만 답변해주세요:
        {{"lookback": "여기에 투자현황 분석과 앞으로의 투자전략 조언을 한글로 작성"}}
        
        주의사항:
        1. 반드시 유효한 JSON 형식이어야 합니다
        2. 따옴표나 중괄호 등 JSON 문법을 정확히 지켜주세요
        3. lookback 키의 값은 반드시 한글로 작성해주세요
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # GPT 응답 전체 내용 출력
            print("\nGPT 응답 원본:")
            print(response.choices[0].message.content)
            print("\n---\n")
            
            # GPT 응답에서 실제 JSON 부분만 추출하기 위한 처리
            response_text = response.choices[0].message.content.strip()
            analysis = json.loads(response_text)
            
            if 'lookback' not in analysis:
                raise ValueError("GPT 응답에 'lookback' 키가 없습니다")
                
            # 3. 가장 최근 매매기록의 lookback 칼럼 업데이트
            cursor.execute("""
                UPDATE trades 
                SET lookback = ? 
                WHERE id = (SELECT id FROM trades ORDER BY timestamp DESC LIMIT 1)
            """, (analysis['lookback'],))
            
            conn.commit()
            conn.close()
            print("매매기록 분석 완료 및 저장됨")
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 에러: {e}")
            print("GPT 응답:", response_text)
            conn.close()
        except Exception as e:
            print(f"remind_records 에러: {e}")
            conn.close()

    except Exception as e:
        print(f"remind_records 에러: {e}")

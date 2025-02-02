import os
from openai import OpenAI
import json
import pyupbit
from dotenv import load_dotenv
from trade.tec_analysis import calculate_indicators, analyze_market_data
from trade.fear_and_greed import get_fear_greed_data
from trade.orderbook_data import get_orderbook_data

# .env 파일 로드
load_dotenv()

# DeepSeek API 클라이언트 설정하기
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 환경변수에서 API 키 가져오기
    base_url="https://api.deepseek.com"  # DeepSeek 서버 주소
)

def get_deepseek_decision(daily_30_analysis, daily_60_analysis, hourly_analysis, fear_greed_data, orderbook_summary):

    # 기본 메시지 구성
    data_content = (
        f"30 Days Analysis: {json.dumps(daily_30_analysis, indent=2)}\n"
        f"60 Days Analysis: {json.dumps(daily_60_analysis, indent=2)}\n"
        f"Hourly Analysis: {json.dumps(hourly_analysis, indent=2)}\n"
        f"Fear and Greed Data: {fear_greed_data}\n"
        f"Orderbook Data: {json.dumps(orderbook_summary)}"
    )

    messages = [
        {
            "role": "system",
            "content": "You are an expert in Bitcoin investing. Analyze the provided data and respond with a trading decision.\n\n"
                      "You must respond ONLY with this exact JSON format:\n"
                      "{\n"
                      "  \"decision\": \"buy\" or \"sell\" or \"hold\",\n"
                      "  \"reason\": \"detailed analysis reason\"\n"
                      "}\n\n"
                      "The decision field MUST be exactly one of: 'buy', 'sell', or 'hold'.\n"
                      "No other format or additional fields are allowed."
        },
        {
            "role": "user",
            "content": data_content
        }
    ]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
        )
        
        # 일반 응답 받기
        content = response.choices[0].message.content
        reasoning = response.choices[0].message.reasoning_content
        
        # 응답이 JSON 형식인지 확인하고 파싱
        try:
            parsed_result = json.loads(content)
            # 추론 과정과 결과를 함께 반환
            return {
                "reasoning": reasoning,
                "decision": parsed_result
            }
        except json.JSONDecodeError:
            print(f"응답이 JSON 형식이 아닙니다: {content}")
            return None
        
    except Exception as e:
        print(f"DeepSeek API 요청 중 오류 발생: {str(e)}")
        return None

if __name__ == "__main__":
    # 데이터 수집
    df_daily_30 = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
    df_daily_30 = calculate_indicators(df_daily_30, is_daily=True)
    
    df_daily_60 = pyupbit.get_ohlcv("KRW-BTC", count=60, interval="day")
    df_daily_60 = calculate_indicators(df_daily_60, is_daily=True)
    
    df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)
    df_hourly = calculate_indicators(df_hourly, is_daily=False)

    # 분석 데이터 준비
    daily_30_analysis, daily_60_analysis, hourly_analysis = analyze_market_data(df_daily_30, df_daily_60, df_hourly)
    fear_greed_data = get_fear_greed_data()
    orderbook_summary = get_orderbook_data()

    # DeepSeek-R1으로 투자 판단 요청
    result = get_deepseek_decision(
        daily_30_analysis,
        daily_60_analysis,
        hourly_analysis,
        fear_greed_data,
        orderbook_summary
    )

    # 결과 출력
    if result:
        print(f"\n🤖 DeepSeek의 추론 과정:")
        print(result["reasoning"])
        print(f"\n\n\n\n⭐️ DeepSeek의 투자 판단:")
        print(f"⭐️결정: {result['decision']['decision']}")
        print(f"⭐️이유: {result['decision']['reason']}")

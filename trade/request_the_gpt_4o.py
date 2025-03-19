from openai import OpenAI
import json
from datetime import datetime
import os

def create_ai_messages(daily_30_analysis, daily_60_analysis, hourly_analysis, fear_greed_data, orderbook_summary):
    """AI에게 보낼 메시지를 생성하는 함수"""
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are an expert in Bitcoin investing. Analyze the provided data and respond with a trading decision.\n\n"
                           "You must respond ONLY with this exact JSON format:\n"
                           "{\n"
                           "  \"decision\": \"buy\" or \"sell\" or \"hold\",\n"
                           "  \"reason\": \"detailed analysis reason\"\n"
                           "}\n\n"
                           "The decision field MUST be exactly one of: 'buy', 'sell', or 'hold'.\n"
                           "No other format or additional fields are allowed."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"30 Days Analysis: {json.dumps(daily_30_analysis, indent=2)}\n"
                           f"60 Days Analysis: {json.dumps(daily_60_analysis, indent=2)}\n"
                           f"Hourly Analysis: {json.dumps(hourly_analysis, indent=2)}\n"
                           f"Fear and Greed Data: {fear_greed_data}\n"
                           f"Orderbook Data: {json.dumps(orderbook_summary)}"
                }
            ]
        }
    ]

    return messages

def process_ai_response(response):
    """AI의 응답을 처리하고 검증하는 함수"""
    result = response.choices[0].message.content
    
    # 토큰 사용량 출력
    print("\n🎯 토큰 사용량:")
    print(f"프롬프트 토큰: {response.usage.prompt_tokens}개")
    print(f"응답 토큰: {response.usage.completion_tokens}개")
    print(f"전체 토큰: {response.usage.total_tokens}개")
    
    # 응답 테스트
    try:
        result = json.loads(result)
        print(f"\n🔍 응답 타입: {type(result)}")
        
        # decision 값이 허용된 값인지 확인
        if result['decision'] not in ['buy', 'sell', 'hold']:
            raise ValueError(f"Invalid decision value: {result['decision']}")
            
    except json.JSONDecodeError:
        print("❌ JSON 파싱 실패!")
        raise
    except KeyError as e:
        print(f"❌ 필수 필드 누락: {e}")
        raise
    except Exception as e:
        print(f"❌ 기타 오류 발생: {e}")
        raise

    return result

def get_ai_decision(daily_30_analysis, daily_60_analysis, hourly_analysis, fear_greed_data, orderbook_summary):
    """AI에게 데이터를 제공하고 투자 판단을 받는 메인 함수"""
    client = OpenAI()
    
    # 메시지 생성
    messages = create_ai_messages(
        daily_30_analysis, 
        daily_60_analysis, 
        hourly_analysis, 
        fear_greed_data, 
        orderbook_summary
    )
    
    # API 호출
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={
            "type": "json_object"
        },
        temperature=0.7,
        max_tokens=500
    )
    
    # 응답 처리 및 반환
    return process_ai_response(response) 
from openai import OpenAI
import json
from datetime import datetime
import os

def prepare_chart_image(image_path):
    """차트 이미지를 인코딩하고 관련 로그를 출력하는 함수"""
    try:
        from trade.img_capture import encode_image_to_base64
        base64_image = encode_image_to_base64(image_path)
        print("\n📸 이미지 인코딩 성공!")
        print(f"인코딩된 이미지 길이: {len(base64_image)} 문자")
        return base64_image
    except FileNotFoundError:
        print("차트 이미지를 찾을 수 없어 :(")
        return None

def create_ai_messages(daily_30_analysis, daily_60_analysis, hourly_analysis, fear_greed_data, orderbook_summary, base64_image):
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
                           "  \"percentage\": number between 1 and 100,\n"
                           "  \"decision\": \"buy\" or \"sell\" or \"hold\",\n"
                           "  \"reason\": \"detailed analysis reason\"\n"
                           "}\n\n"
                           "The decision field MUST be exactly one of: 'buy', 'sell', or 'hold'.\n"
                           "The percentage field represents your confidence level in your decision:\n"
                           "- 100: Absolutely certain about the decision\n"
                           "- 70: Very confident about the decision\n"
                           "- 50: Moderately confident about the decision\n"
                           "- 20: Slightly confident about the decision\n"
                           "- 5: Minimal confidence in the decision\n"
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

    # 이미지가 있으면 메시지에 추가
    if base64_image:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
        print("🎨 API 요청에 이미지가 포함되었어!")
    else:
        print("⚠️ API 요청에 이미지가 포함되지 않았어!")

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

def get_ai_decision(daily_30_analysis, daily_60_analysis, hourly_analysis, fear_greed_data, orderbook_summary, image_path):
    """AI에게 데이터를 제공하고 투자 판단을 받는 메인 함수"""
    client = OpenAI()
    
    # 1. 이미지 준비
    base64_image = prepare_chart_image(image_path)
    
    # 2. 메시지 생성
    messages = create_ai_messages(
        daily_30_analysis, 
        daily_60_analysis, 
        hourly_analysis, 
        fear_greed_data, 
        orderbook_summary, 
        base64_image
    )
    
    # 3. API 호출
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={
            "type": "json_object"
        },
        temperature=0.7,
        max_tokens=500
    )
    
    # 4. 응답 처리 및 반환
    return process_ai_response(response) 
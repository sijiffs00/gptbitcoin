import json
import os
import requests
from datetime import datetime

def create_ai_messages(daily_30_analysis, daily_60_analysis, hourly_analysis, fear_greed_data, orderbook_summary):
    """DeepSeek AI에게 보낼 메시지를 생성하는 함수"""
    # 시스템 메시지와 사용자 메시지 준비
    system_message = {
        "role": "system",
        "content": "You are an expert in Bitcoin investing. Analyze the provided data and respond with a trading decision.\n\n"
                  "You must respond ONLY with this exact JSON format:\n"
                  "{\n"
                  "  \"decision\": \"buy\" or \"sell\" or \"hold\",\n"
                  "  \"reason\": \"detailed analysis reason\"\n"
                  "}\n\n"
                  "The decision field MUST be exactly one of: 'buy', 'sell', or 'hold'.\n"
                  "No other format or additional fields are allowed."
    }
    
    user_message = {
        "role": "user",
        "content": f"30 Days Analysis: {json.dumps(daily_30_analysis, indent=2)}\n"
                  f"60 Days Analysis: {json.dumps(daily_60_analysis, indent=2)}\n"
                  f"Hourly Analysis: {json.dumps(hourly_analysis, indent=2)}\n"
                  f"Fear and Greed Data: {fear_greed_data}\n"
                  f"Orderbook Data: {json.dumps(orderbook_summary)}"
    }
    
    return [system_message, user_message]

def process_ai_response(response_json):
    """DeepSeek AI의 응답을 처리하고 검증하는 함수"""
    # 토큰 사용량 출력
    if "usage" in response_json:
        print("\n🎯 토큰 사용량:")
        print(f"프롬프트 토큰: {response_json['usage']['prompt_tokens']}개")
        print(f"응답 토큰: {response_json['usage']['completion_tokens']}개")
        print(f"전체 토큰: {response_json['usage']['total_tokens']}개")
    
    # 응답 추출 및 검증
    content = response_json["choices"][0]["message"]["content"]
    
    # 응답 테스트
    try:
        result = json.loads(content)
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
    """DeepSeek AI에게 데이터를 제공하고 투자 판단을 받는 메인 함수"""
    # 환경변수에서 API 키 가져오기
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    # API 키가 없으면 오류 메시지 출력
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 환경변수가 설정되지 않았습니다!")
    
    # DeepSeek API 엔드포인트
    url = "https://api.deepseek.com/v1/chat/completions"
    
    # 요청 헤더 설정
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 메시지 생성
    messages = create_ai_messages(
        daily_30_analysis, 
        daily_60_analysis, 
        hourly_analysis, 
        fear_greed_data, 
        orderbook_summary
    )
    
    # 요청 데이터 설정
    data = {
        "model": "deepseek-chat",  # DeepSeek V3 모델 사용
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    # API 요청 보내기
    response = requests.post(url, headers=headers, json=data)
    
    # 응답 상태 확인
    if response.status_code == 200:
        # 응답 처리 및 반환
        return process_ai_response(response.json())
    else:
        error_msg = f"API 요청 실패: 상태 코드 {response.status_code}\n{response.text}"
        print(error_msg)
        raise Exception(error_msg) 
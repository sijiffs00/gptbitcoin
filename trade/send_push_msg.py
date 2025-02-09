import requests
import os
from datetime import datetime
from openai import OpenAI  # OpenAI 추가

# ⭐️ desicion, percentage, reason 을 아이폰 푸시로 발송함.
# ⭐️ 발송하기전에 reason 을 한국어로 번역&요약하는데 gpt-3.5-turbo가 해줌.
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
        print(f"✅ 번역 완료: {translated_text}")  # 번역 결과 로깅
        return translated_text

    except ImportError:
        print("❌ OpenAI 패키지가 설치되지 않았어요! pip install openai 를 실행해주세요.")
        return text
    except Exception as e:
        print(f"❌ GPT 번역 중 오류 발생: {str(e)}")
        print(f"원본 텍스트로 진행합니다: {text}")
        return text

def send_push_notification(decision, percentage, reason):
    """
    트레이딩 결과를 아이폰으로 푸시 알림 보내는 함수
    :param decision: 매수/매도/홀드 결정
    :param percentage: AI가 판단한 확률
    :param reason: AI의 판단 근거
    """
    try:
        # reason을 한국어로 번역하고 요약
        korean_reason = translate_with_gpt(reason)
        
        # Pushover API 키 가져오기
        user_key = os.getenv("PUSHOVER_USER_KEY")
        app_token = os.getenv("PUSHOVER_APP_TOKEN")
        
        # 제목과 메시지 내용 구성
        current_time = datetime.now().strftime("%m/%d %H:%M")
        title = f"{decision} ({percentage}%)"  # 제목에 결정과 확률 표시
        message = f"[{current_time}]\n{korean_reason}"  # 번역된 내용 사용

        # Pushover API로 푸시 알림 전송
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": app_token,
                "user": user_key,
                "message": message,
                "title": title
            }
        )
        
        # 전송 결과 확인
        if response.status_code == 200:
            print("📱 푸시 알림 전송 완료!")
            return True
        else:
            print(f"❌ 푸시 알림 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 푸시 알림 전송 중 오류 발생: {e}")
        return False

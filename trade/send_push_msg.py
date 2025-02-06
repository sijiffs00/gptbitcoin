import requests
import os
from datetime import datetime

def send_push_notification(decision, percentage, reason):
    """
    트레이딩 결과를 아이폰으로 푸시 알림 보내는 함수
    :param decision: 매수/매도/홀드 결정
    :param percentage: AI가 판단한 확률
    :param reason: AI의 판단 근거
    """
    try:
        # Pushover API 키 가져오기
        user_key = os.getenv("PUSHOVER_USER_KEY")
        app_token = os.getenv("PUSHOVER_APP_TOKEN")
        
        # 제목과 메시지 내용 구성
        current_time = datetime.now().strftime("%m/%d %H:%M")
        title = f"{decision} ({percentage}%)"  # 제목에 결정과 확률 표시
        message = f"[{current_time}]\n{reason}"  # 내용에는 시간과 판단 근거만 표시

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

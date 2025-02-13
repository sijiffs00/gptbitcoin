# FCM 푸시 알림 테스트 코드
import os
from dotenv import load_dotenv
from trade.send_push_msg import send_push_notification

# .env 파일 불러오기
load_dotenv()

def test_fcm_notification():
    """FCM 푸시 알림 테스트"""
    try:
        decision = "테스트"
        percentage = 99
        reason = "비트코인 자동매매 봇의 FCM 푸시 알림 테스트입니다. 이 메시지가 보이면 정상적으로 작동하는 거예요!"
        
        print("📱 FCM 푸시 알림 테스트를 시작합니다...")
        success = send_push_notification(decision, percentage, reason)
        
        if success:
            print("✅ FCM 푸시 알림 전송 성공!")
        else:
            print("❌ FCM 푸시 알림 전송 실패!")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_fcm_notification() 
import json
import os
from datetime import datetime

class FCMTokenManager:
    def __init__(self):
        # 프로젝트 루트 경로 찾기
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.token_file = os.path.join(self.root_dir, 'fcm_token.json')
    
    def save_token(self, token: str) -> bool:
        """새로운 FCM 토큰을 저장하는 함수"""
        try:
            data = {
                "fcmToken": token,
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
            
        except Exception as e:
            print(f"❌ FCM 토큰 저장 중 오류 발생: {str(e)}")
            return False
    
    def get_token(self) -> str:
        """저장된 FCM 토큰을 가져오는 함수"""
        try:
            if not os.path.exists(self.token_file):
                return None
                
            with open(self.token_file, 'r') as f:
                data = json.load(f)
                return data.get("fcmToken")
                
        except Exception as e:
            print(f"❌ FCM 토큰 읽기 중 오류 발생: {str(e)}")
            return None
import firebase_admin
from firebase_admin import credentials
import os

def initialize_firebase():
    try:
        # 이미 초기화되어 있는지 확인
        if not firebase_admin._apps:
            # 현재 프로젝트 루트 디렉토리의 credentials 파일 경로
            cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   'firebase-credentials.json')
            
            # Firebase 초기화
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase가 성공적으로 초기화되었습니다!")
            
    except Exception as e:
        print(f"❌ Firebase 초기화 중 오류 발생: {str(e)}")
        raise e
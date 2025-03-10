import os
from dotenv import load_dotenv
import threading
import time
from flask_api_server import run_server
from trade.ai_trading import ai_trading
from trade.remind_records import remind_records

# 0. env 파일 로드
load_dotenv()

if __name__ == '__main__':
    # API 서버를 별도의 스레드로 실행
    api_thread = threading.Thread(target=run_server)
    api_thread.daemon = True  # 메인 프로그램이 종료되면 API 서버도 종료
    api_thread.start()
    print("🚀 API 서버가 시작되었습니다 (포트: 8000)")
    
    print("🤖 트레이딩 봇이 시작됩니다... (OpenAI API 호출 기능은 비활성화됨)")
    while True:
        try:
            # remind_records() 함수 호출 비활성화
            # remind_records()
            
            # ai_trading() 함수 호출 비활성화
            # ai_trading()
            
            print("\n⏰ OpenAI API 호출 기능이 비활성화되었습니다. 서버만 실행 중...")
            time.sleep(3600)  # 1시간(3600초) 대기
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다...")
            break
        except Exception as e:
            print(f"\n❌ 에러 발생: {str(e)}")
            print("⏰ 10초 후에 다시 시작합니다...")
            time.sleep(10)



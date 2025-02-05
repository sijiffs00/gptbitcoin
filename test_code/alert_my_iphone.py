# ⭐️ 
import requests  # HTTP 요청을 보내기 위한 모듈
import time     # 딜레이를 주기 위한 모듈
import os      # 환경변수를 불러오기 위한 모듈
from dotenv import load_dotenv  # .env 파일을 불러오기 위한 모듈
import datetime  # 현재 시간을 다루기 위한 모듈

# .env 파일 불러오기
load_dotenv()

# 환경변수에서 키 불러오기
YOUR_USER_KEY = os.getenv("PUSHOVER_USER_KEY")    # 네 유저 키
YOUR_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")  # 네 앱 토큰

# 무한 반복해서 1분마다 알림을 전송하는 루프
while True:
    try:
        # Pushover API에 POST 요청을 보내서 알림을 전송
        response = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": YOUR_APP_TOKEN,          # 네 앱 토큰
            "user": YOUR_USER_KEY,            # 네 유저 키
            "message": "이 메시지는 1분마다 전송돼!",  # 보내고 싶은 메시지
            "title": "알림",                  # 알림 제목
        })
        # 현재 시간을 원하는 형식으로 포맷팅
        current_time = datetime.datetime.now().strftime("%m.%d (%a) %p %I:%M")
        # 응답 상태코드를 시간과 함께 출력
        log_message = f"{current_time} 알림 전송됨, 상태코드: {response.status_code}"
        print(log_message, flush=True)
        
        # 로그 파일에 기록하기
        with open('logs/alert_log.log', 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception as e:
        # 에러 발생 시 처리
        current_time = datetime.datetime.now().strftime("%m.%d (%a) %p %I:%M")
        error_message = f"{current_time} 알림 전송 중 오류 발생: {e}"
        print(error_message, flush=True)
        
        # 에러도 로그 파일에 기록하기
        with open('logs/alert_log.log', 'a', encoding='utf-8') as f:
            f.write(error_message + '\n')

    # 60초 대기 (1분)
    time.sleep(60) 
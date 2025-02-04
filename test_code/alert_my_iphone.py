# ⭐️ 
import requests  # HTTP 요청을 보내기 위한 모듈
import time     # 딜레이를 주기 위한 모듈
import os      # 환경변수를 불러오기 위한 모듈
from dotenv import load_dotenv  # .env 파일을 불러오기 위한 모듈

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
        # 응답 상태코드를 출력해서 성공/실패 여부 확인
        print("알림 전송됨, 상태코드:", response.status_code)
    except Exception as e:
        # 에러 발생 시 처리
        print("알림 전송 중 오류 발생:", e)

    # 60초 대기 (1분)
    time.sleep(60) 
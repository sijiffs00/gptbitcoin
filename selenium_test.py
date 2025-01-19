from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import os

# Chrome 브라우저 설정하기
chrome_options = Options()
# chrome_options.add_argument('--headless')  # 이 줄을 주석처리하거나 삭제하면 돼!
chrome_options.add_argument('--window-size=1920,1080')  # 화면 크기 설정

# Chrome 드라이버 설정
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

# 업비트 차트 페이지 접속
url = "https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC"
driver.get(url)

# 페이지가 완전히 로딩될 때까지 기다리기
time.sleep(5)  # 5초로 충분해!

# 현재 날짜와 시간으로 파일명 만들기 (예: chart_capture_2501191517)
current_time = datetime.now().strftime("%d%m%y%H%M")
filename = f"chart_capture_{current_time}.png"

# chart 폴더 만들기 (없는 경우)
if not os.path.exists('chart'):
    os.makedirs('chart')

# 스크린샷 찍고 저장하기
driver.save_screenshot(os.path.join('chart', filename))

# 브라우저 종료
driver.quit()
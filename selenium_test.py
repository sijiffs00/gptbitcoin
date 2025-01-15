# 크롬 브라우저를 띄우고 원하는 주소에 접속 --> full screen 버튼을 누르고 --> 화면캡쳐 --> chart폴더에 이미지 저장

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--start-maximized')  # 브라우저 최대화
chrome_options.add_argument('--disable-gpu')  # GPU 하드웨어 가속 비활성화
chrome_options.add_argument('--no-sandbox')  # 샌드박스 비활성화

# chart 폴더 생성
if not os.path.exists('chart'):
    os.makedirs('chart')

# Chrome 드라이버 설정
driver = webdriver.Chrome(options=chrome_options)

# URL 접속
url = "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC"
driver.get(url)

# 명시적 대기 설정 (최대 10초)
wait = WebDriverWait(driver, 10)

try:
    # XPath로 버튼 찾고 클릭
    button_xpath = "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/cq-toggle[1]/span"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    button.click()
    
    # 화면 전환 대기
    time.sleep(2)  # 버튼 클릭 후 화면 전환 대기
    
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join('chart', f'chart_{timestamp}.jpg')
    
    # 스크린샷 저장
    driver.save_screenshot(screenshot_path)
    print(f"스크린샷이 저장되었습니다: {screenshot_path}")
    
    # 브라우저 유지를 위한 무한 대기
    input("브라우저를 종료하려면 Enter 키를 누르세요...")
finally:
    driver.quit()  # 브라우저 종료


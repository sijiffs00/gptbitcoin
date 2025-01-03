import os
from dotenv import load_dotenv
import pyupbit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
from selenium.webdriver.common.by import By

load_dotenv()

# 1. 업비트 객체 생성
access = os.environ.get('UPBIT_ACCESS_KEY')
secret = os.environ.get('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)

# 2. 보유 현금 조회
my_balance = upbit.get_balance("KRW")
print(f"보유 현금: {my_balance:,.0f}원")

# 3. 보유 비트코인 조회
my_btc = upbit.get_balance("KRW-BTC")
print(f"보유 비트코인: {my_btc} BTC")

# 2. 셀레니움 설정 및 스크린샷 촬영
def capture_shot():
    if not os.path.exists('capture'):
        os.makedirs('capture')
    
    # 현재 날짜와 시간으로 파일명 생성
    current_time = datetime.now().strftime('%y%m%d_%H%M')
    filename = f'capture/{current_time}.png'
    
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    
    # 크롬 드라이버 설정
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # 업비트 BTC 차트 페이지 접속
        driver.get('https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC')
        time.sleep(5)
        
        # 지표 버튼 클릭
        print("지표 버튼을 찾는 중...")
        indicator_button = driver.find_element(By.CSS_SELECTOR, 'cq-menu:nth-child(3) span')
        print("지표 버튼 클릭")
        indicator_button.click()
        time.sleep(2)  # 메뉴가 나타날 때까지 대기
        
        # 볼린저 밴드 버튼 클릭
        print("볼린저 밴드 버튼을 찾는 중...")
        bollinger_button = driver.find_element(By.CSS_SELECTOR, 'cq-menu:nth-child(3) cq-menu-dropdown cq-item:nth-child(15)')
        print("볼린저 밴드 버튼 클릭")
        bollinger_button.click()
        time.sleep(2)  # 지표가 적용될 때까지 대기
        
        # 스크린샷 저장
        driver.save_screenshot(filename)
        print(f"스크린샷이 저장되었습니다: {filename}")
        
    finally:
        driver.quit()

# 스크린샷 함수 실행
capture_shot()
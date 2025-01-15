# 크롬 브라우저를 띄우고 원하는 주소에 접속 --> full screen 버튼을 누르고 --> 화면캡쳐 --> chart폴더에 이미지 저장

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--start-maximized')  # 브라우저 최대화
chrome_options.add_argument('--disable-gpu')  # GPU 하드웨어 가속 비활성화
chrome_options.add_argument('--no-sandbox')  # 샌드박스 비활성화

# Chrome 드라이버 설정
driver = webdriver.Chrome(options=chrome_options)

# URL 접속
url = "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC"
driver.get(url)

# 페이지 로딩을 위한 대기 시간
time.sleep(5)


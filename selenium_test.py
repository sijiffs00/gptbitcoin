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
import base64
import requests
import json

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

# OpenAI API 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    
# 올바른 엔드포인트 설정
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def analyze_image_with_openai(image_path):
    """OpenAI Vision API를 사용하여 이미지 분석"""
    # 이미지를 base64로 인코딩
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "이 차트 이미지를 분석해서 주요 특징을 설명해주세요."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    try:
        print("\nAPI 요청 시작...")
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        print(f"API 응답 상태 코드: {response.status_code}")
        result = response.json()
        
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"API 요청 중 오류 발생: {str(e)}"

try:
    # XPath로 버튼 찾고 클릭
    button_xpath = "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/cq-toggle[1]/span"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    button.click()
    
    # 화면 전환 대기
    time.sleep(2)  # 버튼 클릭 후 화면 전환 대기
    
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join('chart', f'chart_{timestamp}.png')
    
    # 스크린샷 저장
    driver.save_screenshot(screenshot_path)
    print(f"스크린샷이 저장되었습니다: {screenshot_path}")
    
    # API 분석 전에 잠시 대기
    time.sleep(1)
    
    # OpenAI Vision API로 이미지 분석
    print("\n=== 이미지 분석 시작 ===")
    analysis_result = analyze_image_with_openai(screenshot_path)
    print("\n=== 이미지 분석 결과 ===")
    print(analysis_result)
    print("\n=== 이미지 분석 완료 ===")
    
    # API 분석이 완료된 후에 사용자 입력 대기
    print("\n모든 처리가 완료되었습니다.")
    input("브라우저를 종료하려면 Enter 키를 누르세요...")
except Exception as e:
    print(f"오류 발생: {str(e)}")
finally:
    driver.quit()

    


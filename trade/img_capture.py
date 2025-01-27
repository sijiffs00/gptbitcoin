from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import base64
from webdriver_manager.chrome import ChromeDriverManager

def capture_chart(chrome_options):
    """
    Selenium을 사용하여 업비트의 비트코인 차트를 캡처하는 함수
    
    Returns:
        bool: 캡처 성공 여부
    """
    print("\n📸 차트 캡처 시작...")
    
    try:
        # Chrome 드라이버 설정
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 트레이딩뷰 차트 페이지로 이동
        driver.get('https://www.tradingview.com/chart/?symbol=UPBIT%3ABTCKRW')
        
        # 페이지 로딩 대기
        time.sleep(10)
        
        # 스크린샷 찍기
        driver.save_screenshot('chart/my_img.png')
        
        # 브라우저 종료
        driver.quit()
        print("📸 차트 캡처 완료!")
        return True
        
    except Exception as e:
        print(f"차트 캡처 중 오류 발생: {e}")
        if 'driver' in locals():
            driver.quit()
        return False

def encode_image_to_base64(image_path):
    """
    이미지 파일을 base64로 인코딩하는 함수
    
    Args:
        image_path (str): 이미지 파일 경로
    
    Returns:
        str: base64로 인코딩된 이미지 문자열
    """
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

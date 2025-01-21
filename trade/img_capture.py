from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import base64

def capture_chart():
    """
    Selenium을 사용하여 업비트의 비트코인 차트를 캡처하는 함수
    
    Returns:
        bool: 캡처 성공 여부
    """
    print("\n📸 차트 캡처 시작...")
    
    # Chrome 옵션 설정
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 브라우저 창을 볼 수 있도록 headless 모드 비활성화
    chrome_options.add_argument('--window-size=1920,1080')  # 화면 크기 설정
    
    try:
        # Chrome 드라이버 설정
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 업비트 차트 페이지 접속 (전체화면 차트 URL 사용)
        url = "https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC"
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(5)  # 5초 대기
        
        # 스크린샷 캡처
        driver.save_screenshot('chart/my_img.png')
        print("📸 차트 캡처 완료!")
        
        driver.quit()
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

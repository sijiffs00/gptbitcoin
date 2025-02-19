import boto3
from datetime import datetime

def upload_chart_to_s3(file_name: str) -> tuple[bool, str]:
    """
    차트 이미지를 S3 버킷에 업로드하는 함수야!
    
    Args:
        file_name (str): 업로드할 로컬 이미지 파일 경로
        
    Returns:
        tuple[bool, str]: (성공 여부, S3에 저장된 파일 경로)
    """
    try:
        s3 = boto3.client('s3')
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f'bitcoin_charts/{current_time}.png'
        bucket_name = 'aibitcoin-chart-img'
        
        # S3에 업로드하기 (Content-Type 지정 및 public-read ACL 추가)
        s3.upload_file(
            file_name,  # 로컬 파일 경로
            bucket_name,  # S3 버킷 이름
            s3_key,  # S3에 저장될 경로/파일명
            ExtraArgs={
                'ContentType': 'image/png',  # Content-Type 지정
                'ContentDisposition': 'inline',  # 브라우저에서 바로 보이도록 설정
                'ACL': 'public-read'  # 파일을 공개적으로 읽을 수 있도록 설정
            }
        )
        
        # 업로드된 파일의 public URL 생성
        url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{s3_key}"
        
        return True, s3_key
        
    except Exception as e:
        print(f"❌ S3 업로드 중 오류 발생: {str(e)}")
        return False, ""

def upload_trading_images_to_s3() -> dict:
    """
    트레이딩 결정(매수/매도/홀드)에 사용되는 이미지들을 S3에 업로드하는 함수
    
    Returns:
        dict: 각 결정에 대한 이미지 URL을 담은 딕셔너리
    """
    try:
        s3 = boto3.client('s3')
        bucket_name = 'aibitcoin-chart-img'
        image_urls = {}
        
        # 업로드할 이미지 파일들
        images = {
            'buy': 'img/buy_img.png',
            'sell': 'img/sell_img.png',
            'hold': 'img/hold_img.png'
        }
        
        for decision, local_path in images.items():
            try:
                s3_key = f'trading_images/{decision}_img.png'
                
                # S3에 업로드
                s3.upload_file(
                    local_path,
                    bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': 'image/png',
                        'ContentDisposition': 'inline',
                        'ACL': 'public-read'
                    }
                )
                
                # URL 생성
                url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{s3_key}"
                image_urls[decision] = url
                print(f"✅ {decision} 이미지 업로드 완료: {url}")
                
            except Exception as e:
                print(f"❌ {decision} 이미지 업로드 실패: {str(e)}")
                
        return image_urls
        
    except Exception as e:
        print(f"❌ S3 연결 중 오류 발생: {str(e)}")
        return {}

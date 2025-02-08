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
                'ACL': 'public-read'  # 파일을 공개적으로 읽을 수 있도록 설정
            }
        )
        
        # 업로드된 파일의 public URL 생성
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        
        return True, s3_key
        
    except Exception as e:
        print(f"❌ S3 업로드 중 오류 발생: {str(e)}")
        return False, ""

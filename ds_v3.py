import os
import requests
import json

# 환경변수에서 API 키 가져오기
api_key = os.environ.get("DEEPSEEK_API_KEY")

# API 키가 없으면 오류 메시지 출력
if not api_key:
    print("DEEPSEEK_API_KEY 환경변수가 설정되지 않았습니다!")
    exit(1)

# Deepseek API 엔드포인트
url = "https://api.deepseek.com/v1/chat/completions"

# 요청 헤더 설정
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# 요청 데이터 설정
data = {
    "model": "deepseek-chat",
    "messages": [
        {
            "role": "user",
            "content": "안녕?"
        }
    ]
}

# API 요청 보내기
try:
    response = requests.post(url, headers=headers, json=data)
    
    # 응답 상태 확인
    if response.status_code == 200:
        # 응답 결과 출력
        result = response.json()
        print("응답 결과:")
        print(result["choices"][0]["message"]["content"])
        
        # 토큰 사용량 출력
        if "usage" in result:
            print("\n토큰 사용량:")
            print(f"입력 토큰 수: {result['usage']['prompt_tokens']}개")
            print(f"출력 토큰 수: {result['usage']['completion_tokens']}개")
            print(f"총 토큰 수: {result['usage']['total_tokens']}개")
    else:
        print(f"API 요청 실패: 상태 코드 {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"오류 발생: {e}")

# 사용 방법 설명
if __name__ == "__main__":
    print("\n이 코드는 Deepseek의 v3 모델에게 '안녕?'이라는 메시지를 보내고 응답을 받아옵니다.")
    print("환경변수 DEEPSEEK_API_KEY에 API 키가 저장되어 있어야 합니다.")

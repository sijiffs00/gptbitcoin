from openai import OpenAI
import os

# DeepSeek API 클라이언트 설정
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY 환경 변수가 설정되지 않았습니다.")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def chat_with_deepseek(prompt):
    try:
        # API 요청 생성
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ],
            stream=False  # 스트리밍 비활성화
        )
        
        # 응답 반환
        return response.choices[0].message.content
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

# 사용 예시
if __name__ == "__main__":
    prompt = "안녕 넌 누구야?"
    response = chat_with_deepseek(prompt)
    print("질문:", prompt)
    print("DeepSeek 응답:", response)

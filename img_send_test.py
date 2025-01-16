# gpt4o API에 이미지파일을 전송함.
# base 64로 인코딩해서 보냄.
# 응답받는거 성공



import base64
from openai import OpenAI
client = OpenAI()

def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image():
    # 이미지 파일 경로
    image_path = 'chart/my_img.png'
    
    try:
        # 이미지를 base64로 인코딩
        base64_image = encode_image_to_base64(image_path)
        
        # API 요청 보내기
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "넌 사용자의 친한 친구야. 항상 반말로 대화하고, 공감을 잘해주는 성격이야. 이미지에 대해 자세히 설명해줘."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이 이미지에 대해 설명해줘."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
        )
        
        # 응답 출력하기
        result = response.choices[0].message.content
        print("\n친구: ", result)
        
    except FileNotFoundError:
        print("이미지 파일을 찾을 수 없어 :(")
    except Exception as e:
        print(f"에러가 발생했어: {str(e)}")

if __name__ == "__main__":
    analyze_image()  
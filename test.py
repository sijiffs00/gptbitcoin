import os
from dotenv import load_dotenv

# 0. env 파일 로드
load_dotenv()

# 1. 업비트 차트 데이터 가져오기 (30일 일봉)
import pyupbit
df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
# print(df.to_json())


# 2. AI에게 데이터 제공하고 판단 받기
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are an expert in Bitcoin investing.\nTell me whether to buy, sell, or hold at the moment based on the chart data provided.\nresponse in json format.\n\nResponse Example :\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"},\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"},\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"},"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": df.to_json()
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\"decision\": \"hold\", \"reason\": \"Bitcoin prices have shown some volatility but appear to be stabilizing. After a peak, there was a slight decline, and the volume of trading is decreasing. This might indicate consolidation before another move. With no major sell-off or breakout signals, holding is advisable.\"}"
        }
      ]
    }
  ],
  response_format={
    "type": "json_object"
  },
)

# API 응답 확인을 위한 출력 추가


result = response.choices[0].message.content

# 3. AI의 판단에 따라 실제로 자동매매 진행하기
import json
result = json.loads(result)
print(f"\n응답 내용 확인:\n{result}") 
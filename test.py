import os
from dotenv import load_dotenv

# 0. env 파일 로드
load_dotenv()

# 1. 업비트 차트 데이터 가져오기 (30일 일봉)
import pyupbit
df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
# print(df.to_json())
print(os.getenv('UPBIT_SECRET_KEY'))  
print(os.getenv('OPENAI_API_KEY'))  

# 2. AI에게 데이터 제공하고 판단 받기

# from openai import OpenAI
# client = OpenAI()

# response = client.chat.completions.create(
#   model="gpt-4",
#   messages=[
#     {
#       "role": "system",
#       "content": [
#         {
#           "type": "text",
#           "text": "You are an expert in Bitcoin investing.\nTell me whether to buy, sell, or hold at the moment based on the chart data provided.\nresponse in json format.\n\n    Response Example :\n    {\"decision\": \"buy\", \"reason\": \"some technical reason\"},\n    {\"decision\": \"buy\", \"reason\": \"some technical reason\"},\n    {\"decision\": \"buy\", \"reason\": \"some technical reason\"}"
#         }
#       ]
#     }
#   ],
#   response_format={
#     "type": "json_object"
#   },
#   temperature=1,
#   max_completion_tokens=2048,
#   top_p=1,
#   frequency_penalty=0,
#   presence_penalty=0
# )
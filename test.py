import os
from dotenv import load_dotenv
load_dotenv()

print(os.getenv("UPBIT_ACCESS_KEY"))
print(os.getenv("UPBIT_SECRET_KEY"))
print(os.getenv("OPENAI_API_KEY"))


# 너는 비트코인 투자 전문가야.
# 제공된 차트 데이터를 기반으로 현재 buy, sell, hold 중 어떤 선택을 해야할지 알려줘
# JSON 형식으로 대답해

# You are an expert in Bitcoin investing. Tell me whether to buy, sell, or hold at the moment based on the chart data provided.
# JSON 형식으로 대답해
# Response Example : {"decision": "buy", "reason": "some technical reason"}



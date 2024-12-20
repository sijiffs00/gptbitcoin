import os
from dotenv import load_dotenv
import pyupbit

load_dotenv()

# 1. 업비트 객체 생성
access = os.environ.get('UPBIT_ACCESS_KEY')
secret = os.environ.get('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)

# 2. 보유 현금 조회
my_balance = upbit.get_balance("KRW")
print(f"보유 현금: {my_balance:,.0f}원")

# 3. 보유 비트코인 조회
my_btc = upbit.get_balance("KRW-BTC")
print(f"보유 비트코인: {my_btc} BTC")
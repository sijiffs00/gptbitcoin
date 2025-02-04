# ⭐️ 오늘 한국 주식시장이 열리는 날인지, 지금 거래가능한 시간인지 여부를 알아내는게 미션
#   이 코드 돌리면 다음과 같이 나옴
#       오늘 한국 주식시장은 열리는 날인가? True
#       지금은 거래 가능한 시간인가? False



import pandas as pd
import pandas_market_calendars as mcal

# 한국 주식시장을 위한 캘린더 객체 생성
# 'XKRX'는 한국 거래소(KRX)를 의미해.
krx = mcal.get_calendar('XKRX')

# 현재 한국 시간을 Asia/Seoul 타임존으로 받음
now = pd.Timestamp.now('Asia/Seoul')

# 오늘 날짜를 "YYYY-MM-DD" 문자열로 변환함
today_str = now.strftime('%Y-%m-%d')

# 오늘의 거래 스케줄을 가져옴.
# 스케줄이 비어있으면 오늘은 거래하지 않는 날(휴일, 주말)이야.
schedule = krx.schedule(start_date=today_str, end_date=today_str)
if schedule.empty:
    is_trading_day = False
    is_market_open = False
else:
    is_trading_day = True
    # pandas_market_calendars 라이브러리에서 스케줄은 UTC 시간으로 되어있어.
    # 그래서 현재 시간(now)을 UTC로 변환해줘야 해.
    now_utc = now.tz_convert('UTC')
    try:
        # timestamp와 schedule을 함께 전달해줘야 해.
        is_market_open = krx.open_at_time(timestamp=now_utc, schedule=schedule)
    except ValueError:
        # ValueError 예외는 timestamp가 스케줄 범위에 없다는 뜻이야.
        is_market_open = False

# 결과 출력
print("오늘 한국 주식시장은 열리는 날인가?", is_trading_day)
print("지금은 거래 가능한 시간인가?", is_market_open)


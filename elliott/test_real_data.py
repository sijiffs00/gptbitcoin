import pandas as pd
import pyupbit
from elliott_waves import ElliottWaveAnalyzer

# 업비트에서 비트코인 일봉 데이터 가져오기
df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=365)  # 최근 1년 데이터

# 데이터 전처리
df = df.reset_index()  # index를 컬럼으로 변환
df = df.rename(columns={'index': 'date', 'close': 'close'})

# 엘리엇 파동 분석기 생성
analyzer = ElliottWaveAnalyzer()

# 파동 패턴 찾기
results = analyzer.find_pattern(df)

# 결과 출력
print("\n=== 비트코인 엘리엇 파동 분석 결과 ===")
print(f"분석 기간: {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")
print(f"발견된 파동 수: {len(results['waves'])}")

for wave in results['waves']:
    print(f"\n파동 {wave['wave_num']}:")
    print(f"시작일: {wave['start_date']}")
    print(f"종료일: {wave['end_date']}")
    print(f"시작가격: {wave['start_price']:,.0f}원")
    print(f"종료가격: {wave['end_price']:,.0f}원")
    
    # 가격 변화율 계산
    change = ((wave['end_price'] - wave['start_price']) / wave['start_price']) * 100
    print(f"가격 변화: {change:+.2f}%")

# 파동 시각화
analyzer.plot_waves(df) 
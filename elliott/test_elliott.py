import pandas as pd
import numpy as np
from elliott_waves import ElliottWaveAnalyzer

# 테스트용 데이터 생성
dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
# 임의의 가격 데이터 생성 (파동 패턴과 비슷하게)
prices = [
    *np.linspace(40000, 50000, 60),  # 파동 1: 상승
    *np.linspace(50000, 45000, 30),  # 파동 2: 하락
    *np.linspace(45000, 60000, 90),  # 파동 3: 큰 상승
    *np.linspace(60000, 55000, 40),  # 파동 4: 하락
    *np.linspace(55000, 65000, 50)   # 파동 5: 상승
]

# 약간의 노이즈 추가
prices = np.array(prices) + np.random.normal(0, 500, len(prices))

# DataFrame 생성
df = pd.DataFrame({
    'date': dates[:len(prices)],
    'close': prices
})

# 엘리엇 파동 분석기 생성
analyzer = ElliottWaveAnalyzer()

# 파동 패턴 찾기
results = analyzer.find_pattern(df)

# 결과 출력
print("\n=== 엘리엇 파동 분석 결과 ===")
print(f"발견된 파동 수: {len(results['waves'])}")
for wave in results['waves']:
    print(f"\n파동 {wave['wave_num']}:")
    print(f"시작일: {wave['start_date']}")
    print(f"종료일: {wave['end_date']}")
    print(f"시작가격: {wave['start_price']:.2f}")
    print(f"종료가격: {wave['end_price']:.2f}")

# 파동 시각화
analyzer.plot_waves(df) 
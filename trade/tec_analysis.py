import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands

def calculate_indicators(df, is_daily=True):
    """
    기술적 지표들을 계산하여 DataFrame에 추가
    """
    # RSI 계산
    rsi = RSIIndicator(df['close'], window=14)
    df['rsi'] = rsi.rsi()
    
    # MACD 계산
    macd = MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    
    # 볼린저 밴드 계산
    bollinger = BollingerBands(df['close'])
    df['bb_high'] = bollinger.bollinger_hband()
    df['bb_low'] = bollinger.bollinger_lband()
    
    # 이동평균선
    sma = SMAIndicator(df['close'], window=20)
    df['sma_20'] = sma.sma_indicator()
    
    return df

def analyze_market_data(df_daily, df_hourly):
    """
    일봉/시간봉 데이터를 분석하여 요약된 결과를 반환
    
    Args:
        df_daily (DataFrame): 일봉 데이터 (RSI, MACD, BB, MA20 포함)
        df_hourly (DataFrame): 시간봉 데이터 (RSI, MACD 포함)
    
    Returns:
        tuple: (daily_analysis, hourly_analysis) - 일봉과 시간봉 분석 결과
    """
    daily_analysis = {
        "current_price": df_daily['close'].iloc[-1],
        "price_change": f"{((df_daily['close'].iloc[-1] / df_daily['close'].iloc[-2]) - 1) * 100:.2f}%",
        "volume": df_daily['volume'].iloc[-1],
        "indicators": {
            "rsi": {
                "value": round(df_daily['rsi'].iloc[-1], 2),
                "signal": "과매수" if df_daily['rsi'].iloc[-1] > 70 else "과매도" if df_daily['rsi'].iloc[-1] < 30 else "중립"
            },
            "macd": {
                "value": round(df_daily['macd'].iloc[-1], 2),
                "signal": round(df_daily['macd_signal'].iloc[-1], 2) if not pd.isna(df_daily['macd_signal'].iloc[-1]) else 0,
                "trend": "상승신호" if df_daily['macd'].iloc[-1] > df_daily['macd_signal'].iloc[-1] else "하락신호"
            },
            "bollinger_bands": {
                "upper": round(df_daily['bb_high'].iloc[-1], 2),
                "lower": round(df_daily['bb_low'].iloc[-1], 2),
                "position": "상단돌파" if df_daily['close'].iloc[-1] > df_daily['bb_high'].iloc[-1] else 
                           "하단돌파" if df_daily['close'].iloc[-1] < df_daily['bb_low'].iloc[-1] else "밴드내"
            },
            "ma20": {
                "value": round(df_daily['sma_20'].iloc[-1], 2),
                "trend": "상승추세" if df_daily['close'].iloc[-1] > df_daily['sma_20'].iloc[-1] else "하락추세"
            }
        }
    }

    hourly_analysis = {
        "current_price": df_hourly['close'].iloc[-1],
        "price_change": f"{((df_hourly['close'].iloc[-1] / df_hourly['close'].iloc[-2]) - 1) * 100:.2f}%",
        "volume": df_hourly['volume'].iloc[-1],
        "indicators": {
            "rsi": {
                "value": round(df_hourly['rsi'].iloc[-1], 2),
                "signal": "과매수" if df_hourly['rsi'].iloc[-1] > 70 else "과매도" if df_hourly['rsi'].iloc[-1] < 30 else "중립"
            },
            "macd": {
                "value": round(df_hourly['macd'].iloc[-1], 2),
                "signal": round(df_hourly['macd_signal'].iloc[-1], 2) if not pd.isna(df_hourly['macd_signal'].iloc[-1]) else 0,
                "trend": "상승신호" if df_hourly['macd'].iloc[-1] > df_hourly['macd_signal'].iloc[-1] else "하락신호"
            }
        }
    }
    
    return daily_analysis, hourly_analysis

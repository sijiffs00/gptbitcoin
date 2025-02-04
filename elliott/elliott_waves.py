import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Tuple

class ElliottWaveAnalyzer:
    """엘리엇 파동 패턴을 분석하는 클래스"""
    
    def __init__(self):
        self.waves = []
        self.min_wave_length = 5  # 최소 파동 길이
        self.max_retracement = 0.618  # 최대 조정 비율 (피보나치)
        
    def find_pattern(self, 
                    df: pd.DataFrame, 
                    price_column: str = 'close',
                    date_column: str = 'date',
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Dict:
        """
        주어진 가격 데이터에서 엘리엇 파동 패턴을 찾습니다.
        """
        # 데이터 전처리
        df = df.copy()
        if start_date:
            df = df[df[date_column] >= start_date]
        if end_date:
            df = df[df[date_column] <= end_date]
            
        prices = df[price_column].values
        dates = df[date_column].values
        
        # 극값(피크와 저점) 찾기
        extremes = self._find_extremes(prices)
        
        # 파동 패턴 찾기
        waves = self._identify_waves(prices, extremes)
        
        # 파동 필터링 (엘리엇 규칙 적용)
        valid_waves = self._filter_waves(prices, waves)
        
        self.waves = [{
            'start_idx': wave[0],
            'end_idx': wave[1],
            'start_date': dates[wave[0]],
            'end_date': dates[wave[1]],
            'start_price': prices[wave[0]],
            'end_price': prices[wave[1]],
            'wave_num': i+1
        } for i, wave in enumerate(valid_waves)]
        
        return {
            'waves': self.waves,
            'extremes': extremes
        }
    
    def _find_extremes(self, prices: np.ndarray) -> List[int]:
        """가격 데이터에서 극값(피크와 저점)의 인덱스를 찾습니다."""
        extremes = []
        for i in range(1, len(prices)-1):
            # 피크나 저점 찾기
            if (prices[i-1] < prices[i] > prices[i+1]) or \
               (prices[i-1] > prices[i] < prices[i+1]):
                extremes.append(i)
        return extremes
    
    def _identify_waves(self, prices: np.ndarray, extremes: List[int]) -> List[Tuple[int, int]]:
        """극값들을 사용해서 가능한 파동들을 식별합니다."""
        waves = []
        for i in range(len(extremes)-1):
            # 파동의 시작과 끝점
            start_idx = extremes[i]
            end_idx = extremes[i+1]
            
            # 최소 길이 체크
            if end_idx - start_idx >= self.min_wave_length:
                waves.append((start_idx, end_idx))
        
        return waves
    
    def _filter_waves(self, prices: np.ndarray, waves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """엘리엇 파동 규칙에 맞는 파동만 필터링합니다."""
        valid_waves = []
        
        for i in range(len(waves)-4):  # 5개의 파동을 찾기 위해
            wave1 = waves[i]
            wave2 = waves[i+1]
            wave3 = waves[i+2]
            wave4 = waves[i+3]
            wave5 = waves[i+4]
            
            # 규칙 1: 파동2는 파동1의 시작점보다 낮지 않아야 함
            if prices[wave2[1]] <= prices[wave1[0]]:
                continue
                
            # 규칙 2: 파동3은 파동1보다 길어야 함
            if (wave3[1] - wave3[0]) <= (wave1[1] - wave1[0]):
                continue
                
            # 규칙 3: 파동4는 파동1의 끝점보다 낮지 않아야 함
            if prices[wave4[1]] <= prices[wave1[1]]:
                continue
                
            # 규칙 4: 파동2의 조정 비율 체크
            wave1_height = abs(prices[wave1[1]] - prices[wave1[0]])
            wave2_retracement = abs(prices[wave2[1]] - prices[wave2[0]]) / wave1_height
            if wave2_retracement > self.max_retracement:
                continue
            
            valid_waves.extend([wave1, wave2, wave3, wave4, wave5])
            break
            
        return valid_waves
    
    def plot_waves(self, 
                  df: pd.DataFrame,
                  price_column: str = 'close',
                  date_column: str = 'date'):
        """찾은 엘리엇 파동 패턴을 시각화합니다."""
        plt.figure(figsize=(15, 7))
        
        # 가격 데이터 플롯
        plt.plot(df[date_column], df[price_column], 'gray', label='Price', alpha=0.5)
        
        # 파동 패턴 플롯
        colors = ['blue', 'red', 'green', 'purple', 'orange']
        if self.waves:
            for wave, color in zip(self.waves, colors):
                start_date = wave['start_date']
                end_date = wave['end_date']
                start_price = wave['start_price']
                end_price = wave['end_price']
                
                plt.plot([start_date, end_date], 
                        [start_price, end_price], 
                        color=color, 
                        linewidth=2, 
                        label=f'Wave {wave["wave_num"]}')
                
                # 파동 번호 표시
                mid_date = pd.to_datetime(start_date) + (pd.to_datetime(end_date) - pd.to_datetime(start_date))/2
                mid_price = (start_price + end_price)/2
                plt.annotate(f'{wave["wave_num"]}', 
                           (mid_date, mid_price),
                           xytext=(10, 10),
                           textcoords='offset points')
        
        plt.title('Elliott Wave Pattern Analysis')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show() 
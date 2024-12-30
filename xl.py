import os
import pandas as pd

file_path = '/Users/sojung/Downloads/sea_turtle_soup.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(df)
else:
    print("파일을 찾을 수 없습니다.")
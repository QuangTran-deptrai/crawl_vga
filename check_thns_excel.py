import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_excel('d:\\crawlVGA\\THNS_VGA_Report.xlsx')
for idx, name in enumerate(df['Tên sản phẩm'].head(30)):
    print(f"{idx+1}. {name}")

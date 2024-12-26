import requests
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

# 獲取 K 線數據
def get_kline_data(symbol, limit=120):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=15m&limit={limit}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        klines = response.json()
        df = pd.DataFrame(klines, columns=["Open Time", "Open", "High", "Low", "Close", "Volume", 
                                           "Close Time", "Quote Asset Volume", "Number of Trades", 
                                           "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"])
        df["Open Time"] = pd.to_datetime(df["Open Time"], unit='ms')
        df.set_index("Open Time", inplace=True)
        df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
        return df
    except Exception as e:
        print(f"獲取 {symbol} 的 K 線數據時出現錯誤: {e}")
        return None

def plot_kline(df, symbol, image_path):
    # 計算均線
    df['MA30'] = df['Close'].rolling(window=30).mean()
    df['MA45'] = df['Close'].rolling(window=45).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()

    # 時間+8小時
    df = df.copy()
    df.index = df.index + pd.Timedelta(hours=8)

    # 建立K線圖和成交量圖
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10),
                                   gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.05})

    # 繪製 K 線
    for idx, row in df.iterrows():
        color = '#FFC000' if row['Close'] > row['Open'] else '#5F6E96'
        center = mdates.date2num(idx)  # 獲取日期對應的數值作為中心點

        # 繪製蠟燭圖
        ax1.add_patch(Rectangle((center - 0.005, min(row['Open'], row['Close'])), 0.01,
                                abs(row['Close'] - row['Open']), color=color))

        # 繪製上下引線
        ax1.plot([center, center], [row['Low'], row['High']], color=color, linewidth=0.5)

    # 繪製均線
    ax1.plot(df.index, df['MA30'], color='#5093C0', linewidth=1.6)
    ax1.plot(df.index, df['MA45'], color='#5093C0', linewidth=1.6)
    ax1.plot(df.index, df['MA60'], color='#2B5877', linewidth=1.6)

    # 格式化 K 線圖
    symbol = re.sub(r'USDT$', '', symbol) 
    ax1.set_title(symbol, fontsize=24)
    ax1.set_ylabel("Price", fontsize=12)
    ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    ax1.spines['top'].set_visible(False)  # 移除上框線
    ax1.spines['right'].set_visible(False)  # 移除右框線

    # 繪製成交量
    for idx, row in df.iterrows():
        color = mcolors.to_rgba('#FFC000', alpha=0.5) if row['Close'] > row['Open'] else mcolors.to_rgba('#5F6E96', alpha=0.5)
        ax2.bar(mdates.date2num(idx), row['Volume'], color=color, width=0.01)


    # 格式化成交量圖
    ax2.set_ylabel("Volume", fontsize=12)
    ax2.set_xlim(ax1.get_xlim())
    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=3)) 
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # 標籤為時:分
    ax2.spines['top'].set_visible(False)  # 移除上框線
    ax2.spines['right'].set_visible(False)  # 移除右框線

    # 保存圖表
    plt.savefig(image_path)
    plt.close()

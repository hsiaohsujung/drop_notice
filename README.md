# 🚀 Crypto Notify  
> 自動追蹤強勢虛擬貨幣並發送 LINE 通知

使用 Python 開發的自動化程式，每天爬取虛擬貨幣資料與強勢標的，並在符合自訂的條件門檻（如：價格、交易量、漲跌幅）時，將資訊（價格、交易量、漲跌幅、K 線圖）透過 **LINE Notify** 發送通知。減少監控時間與掌握交易機會 📈

---

## 📦 程式功能

- 🔍 自動爬取虛擬貨幣標的，並串接幣安API
- 🎯 自訂篩選條件（價格、漲跌幅、交易量等）
- 🕹️ 可自由開啟/關閉爬蟲功能(如關閉，可以自行輸入想監控的標的)
- 📊 自動繪製 K 線圖
- 📩 即時透過 LINE 通知推送標的資訊

---

## 🛠️ 使用技術與套件

主要 Python 套件如下：

| 套件名稱       | 功能說明                  |
|----------------|--------------------------|
| `selenium`     | 爬取網頁資料、取得強勢標的 |
| `requests`     | 抓取資料、連接 API        |
| `pandas`       | 數據處理與過濾            |
| `matplotlib`   | 繪製圖表／K 線圖          |
| `schedule`     | 任務排程，每日定時執行     |
| `line_notify`  | 發送通知與管理權杖         |

---

## ⚙️ 安裝與執行

▶️ 執行主程式
```python daily_schedule.py ```

🧩 參數設定  
編輯 drop_notice.py 檔案，設定以下內容：    
📊 參數門檻：設定價格/漲跌幅/交易量等條件  
🔄 自動爬蟲：True/False，是否自動抓取強勢標的  
🖼️ 傳送圖片：True/False  

💬 LINE 通知整合
使用 LINE Notify 串接：  
取得你的 LINE 權杖（access token）  
程式會自動發送符合條件的幣種資訊與 K 線圖至 LINE  

# 終端機查詢chrome使用者
```bash
chrome --profile-directory="Default"
```

通知範例圖如下：
![image](https://github.com/hsiaohsujung/drop_notice/blob/master/alert_info.png)

![image](https://github.com/hsiaohsujung/drop_notice/blob/master/k_line.jpg)

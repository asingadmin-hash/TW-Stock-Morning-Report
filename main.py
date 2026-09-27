import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types

def send_email(subject, body):
    sender_email = "asingadmin@gmail.com"
    # ⭐ 在這裡設定多個收件人信箱（想加幾個就加幾個）
    receiver_emails = [
        "asingadmin@gmail.com",
        "Kenfungkenfungkenfung@gmail.com",
    ]

    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not app_password:
        print("【警告】找不到 GMAIL_APP_PASSWORD 環境變數，無法發送郵件！")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg, to_addrs=receiver_emails)
        server.quit()
        print(f"✅ 成功發送台股晨報 Email 至：{', '.join(receiver_emails)}！")
    except Exception as e:
        print(f"❌ 發送郵件失敗：{e}")

def run_tw_stock_agent():
    if not os.environ.get("GEMINI_API_KEY"):
        print("錯誤：找不到 GEMINI_API_KEY 環境變數")
        return

    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 台股策略晨報 Agent 執行中...")
    client = genai.Client()

    available_models = [
        m.name.replace("models/", "")
        for m in client.models.list()
        if "generateContent" in m.supported_actions
    ]
    available_models.sort(key=lambda x: (0 if "flash" in x else 1, x), reverse=False)

    # === 台股策略晨報 Prompt ===
    morning_prompt = '''請根據今天的日期，使用 Google 搜尋工具即時檢索最新的財經新聞、總經數據與盤後籌碼資訊，然後依照以下架構產出今日的【台股策略晨報】。

# 【檢索任務：請先搜尋以下資訊】

在產出報告之前，請務必先用 Google 搜尋取得以下最新資料：
1. 昨夜美股四大指數（道瓊、S&P500、那斯達克、費半）收盤表現
2. 台積電 ADR (TSM) 收盤價與漲跌幅
3. 台指期夜盤最新收盤點數與漲跌
4. 台灣最新出口數據（年增率）、外銷訂單
5. 台灣央行最新貨幣政策動向、M1B/M2 年增率
6. 主計總處最新 GDP 預測或修正
7. AI / 半導體 / 雲端服務商（CSP）最新資本支出或財報動態
8. 外資近期在台股的買賣超趨勢
9. 台股 0050、0056 最新報價
10. 國際油價、美元指數 (DXY)、美國 10 年期公債殖利率、VIX

---

# 【報告輸出格式】

## 1. 核心指標量化監控矩陣

請建立一個表格，彙整今日關鍵領先訊號：

| 領先指標維度 | 追蹤核心指標 | 當前趨勢與數值 | 台股訊號 (偏多/中立/警訊) | 影響時間維度 |
|---|---|---|---|---|
| 資金面 (Liquidity) | M1B/M2 年增率、超額儲蓄、外資動向 | （填入最新數據） | | 中長線 |
| 基本面動能 (Fundamentals) | 出口年增率、外銷訂單、資本支出 | （填入最新數據） | | 中長線 |
| 外部與匯率 (FX & Macro) | 美元指數、台幣匯率、美債殖利率 | （填入最新數據） | | 短中線 |
| 國際股市連動 | 美股四大指數、費半、台積電 ADR | （填入最新數據） | | 短線 |
| 盤前情緒 | 台指期夜盤、VIX、外資期貨未平倉 | （填入最新數據） | | 極短線 |

## 2. 領先指標深層解讀

### 游資動能與資金池水位
解讀當前儲蓄、貨幣供給（M1B/M2）或債券/外匯市場變化，評估資金回流股市或推升資產行情的潛能。

### 科技資本支出與產業鏈展望
檢視 AI/半導體/雲端服務商（CSP）的資本支出趨勢，是否延續「投資成長帶動獲利成長」的正向循環。

### 潛在結構性風險
留意匯率大幅波動對出口毛利率的侵蝕、國內資金過剩引發的資產泡沫警戒，或產業 K 型復甦（科技強、傳統產業弱）的潛在隱憂。

## 3. 產業族群與標的聯動推演

### 高敏感受惠族群
受惠資本支出擴張的先進製程、高階載板、AI 伺服器供應鏈，或受惠資金行情的權值股與高息資產。

### 需防範修正風險族群
受排擠或毛利承壓的板塊。

### ETF 快覽
- **0050 (元大台灣50)**：最新報價、技術面位階、短評
- **0056 (元大高股息)**：最新報價、殖利率概況、短評

## 4. 每日操盤戰略結論

- **一句話總結**：今日「領先指標綜合溫度計」（如：資金與出口雙輪驅動，維持偏多格局；或指標過熱，提防乖離修正）。
- **具體配置建議**：給投資人的配置或避險行動建議，用大白話講清楚。
- **今日風險提醒**：今日盤中或晚間是否有重大數據將公布？操作上應注意哪些風險？

---

# 【紀律要求】

1. 不要編數字。找不到的數據請標註「數據未更新」或「滯後至 [日期]」。
2. 結論用大白話，該說「減碼」就說「減碼」，不要打太極。
3. 請先確認今天日期，確保所有數據的時效性。
4. 每項數據都要標註資料日期或來源時間。
'''

    success = False
    report_content = ""
    for target_model in available_models:
        print(f"嘗試使用模型: {target_model} ...")
        try:
            response = client.models.generate_content(
                model=target_model,
                contents=morning_prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    temperature=0.2,
                    system_instruction=(
                        "你是一位精通台灣總體經濟、科技供應鏈與台股資金面的資深量化研究員與台股策略分析師。"
                        "台灣經濟高度受「AI/半導體出口」、「資本支出/投資成長」以及「超額儲蓄衍生的充沛流動性（資金面）」驅動。"
                        "請務必使用 Google 搜尋工具取得最新的財經數據與新聞，嚴禁捏造數據。"
                        "請依據每日最新財經新聞、總經數據與盤後籌碼，提煉出台股的中長期領先指標與當日短線預警。"
                        "所有分析結論必須精準、有力、可操作，避免空洞套話。"
                    )
                )
            )
            report_content = response.text
            success = True
            print("成功取得台股晨報！")
            break
        except Exception:
            continue

    if success:
        print("\n【台股策略晨報】\n")
        print(report_content)
        send_email(
            subject=f"📈 [台股策略晨報] 領先指標與操盤戰略 ({time.strftime('%Y-%m-%d %H:%M')})",
            body=report_content
        )
    else:
        print("抱歉，目前沒有可用的模型能完成此任務。")

if __name__ == "__main__":
    run_tw_stock_agent()

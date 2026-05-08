# 異環每日任務輔助程式（可下載即跑模板）

這份專案提供一個「客戶下載後可直接執行」的基礎版本，目標是：
- 讀取目前遊戲狀態（`state.json`）
- 自動比對異環每日任務規則（`rules.example.json`）
- 依規則執行對應動作（預設為安全 `dry-run`，只列印不實際操作）

> ⚠️ 請務必先確認《異環》服務條款是否允許自動化。

---

## 1) 客戶快速使用（Python 版）

### 步驟 A：下載並解壓
把下列檔案放在同一個資料夾：
- `game_daily_assistant.py`
- `rules.example.json`

### 步驟 B：建立狀態檔 `state.json`

```json
{
  "game": "yihuan",
  "screen": "main",
  "daily_sign_in_available": true,
  "mail_reward_available": true,
  "stamina_enough": true,
  "bounty_remaining": true,
  "stamina_purchase_left": true
}
```

### 步驟 C：執行

```bash
python3 game_daily_assistant.py --rules rules.example.json --state state.json
```

程式會持續輪詢，並輸出觸發規則與動作。

---

## 2) 打包成單一可執行檔（給不會安裝 Python 的客戶）

在你的打包機器上執行：

```bash
python3 -m pip install pyinstaller
pyinstaller --onefile game_daily_assistant.py
```

完成後可把 `dist/game_daily_assistant`（Windows 會是 `.exe`）連同 `rules.example.json` 一起交付客戶。

客戶執行方式：

```bash
./game_daily_assistant --rules rules.example.json --state state.json
```

---

## 3) 目前內建的異環規則

- `claim_daily_sign_in`：簽到可領時領取
- `claim_mail_reward`：郵件可領時領取
- `run_quick_bounty`：體力足夠且委託未做完時快速委託
- `buy_daily_stamina`：仍可購買每日體力時執行一次

---

## 4) 客製化入口（你可再擴充給客戶）

1. 在 `YiHuanStateProvider.get_state()` 接入 OCR / 螢幕辨識 / 外部偵測器。
2. 在 `ActionExecutor.execute()` 連接你允許的操作方式（例如合法巨集）。
3. 在 `rules.example.json` 新增更多任務判斷條件與動作。

---

## 5) 安全建議

- 先用預設 dry-run 測試流程正確性。
- 每條規則請設定 `cooldown_sec`，避免重複觸發。
- 建議先在測試帳號或低風險場景驗證。

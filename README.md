# 逆轉金幣 Reverse Coin Battle（改編對戰遊戲）

> 測試版推廣版本 請勿銷售利用｜改編萬代逆轉金幣

依專家規則製作的改編對戰遊戲。金幣圖、場地圖、圖示皆為原創示意圖，金幣名稱為改編用中文名。

**直接玩：** https://mchpoker619.github.io/reverse-coin-game/

| 資料夾 | 內容 |
|---|---|
| `docs/` | 網站版（3D／2D，手機可玩，含線上對戰）與下載區 `docs/download/` |
| `python-2d/` | Python 2D 桌面版（pygame-ce）原始碼 |
| `windows-3d/` | 3D 電腦版遊戲檔 |
| `android/` | Android Studio 專案（WebView 單機版），Build → Build APK |
| `web-source/` | 網頁版原始碼與打包腳本（`build_offline.py`、`build_2d_web.py`） |

> Windows 版與 Python 版的啟動／安裝腳本（`.bat`、`.ps1`）放在下載區的 zip 裡：
> `docs/download/ReverseCoin3D_Windows.zip`、`docs/download/ReverseCoin2D_Python.zip`、`docs/download/ReverseCoin_Android_Project.zip`

## 遊戲重點
- 後拉發射（彈弓式）或點選式（點方向 → 確定方向 → 力量條 → 精準度），← → 360° 調整方向
- 撞球式碰撞與旋轉、撞擊火花／震動／頓格特效
- 打中弱點會彈起翻轉：每次 5～7 圈、落地加速，約 15% 會再小彈一次慢慢翻（正反面仍各 1/2）
- 每回合 30 秒、全場 8 分鐘；香港大賽規則、可開關出界
- 雙人同機、對戰電腦（4 種強度）、兩支手機或手機與電腦線上對戰＋觀戰連結
- 場地：放置區域圖層（金幣位置與間隔）可開關；底圖可換成自己的照片（只在自己畫面）
- 新手教學、圖解規則、音效與背景音樂（`sounds/` 可自行替換）
- 收藏與抽包：新玩家有 3 組起始預組，其他金幣靠扭蛋機抽（4 個卡池，RR 1%／BBR 3%／BR 6%／R 30%／C 60%），組隊只能選已收藏的金幣
- 抽包券：線上對戰勝 +3、和 +2、敗 +1，贏電腦 +1；主選單與扭蛋機顯示「可抽 N 次」
- 線上商城：每日登入禮、抽包券、新手禮包、月卡（測試版不收費，按下直接取得）
- 會員：註冊／登入／登出／訪客，每個帳號各自的收藏、抽包券、戰績、訂單（目前存在本機瀏覽器；雲端會員與金流待接）

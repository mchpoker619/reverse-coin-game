# 逆轉金幣 3D — Android 專案（WebView 單機版）

測試版推廣版本 請勿銷售利用。

這是一個 Android Studio 專案：一個全螢幕 WebView，載入 `app/src/main/assets/index.html`（就是 3D 單機版 HTML，已內建 three.js 與所有圖片），手機不需要網路。

## 產生 APK

1. 安裝 Android Studio（Koala 或更新版）。
2. File → Open，選這個資料夾。第一次開啟會自動下載 Gradle 與 Android 外掛，等它同步完成。
3. 選單 Build → Build App Bundle(s) / APK(s) → Build APK(s)。
4. 完成後點通知裡的「locate」，APK 在 `app/build/outputs/apk/debug/app-debug.apk`。
5. 把 APK 傳到手機安裝（需允許「安裝未知來源的應用程式」）。

## 更新遊戲內容

重新產生 3D 單機版 HTML 後，覆蓋 `app/src/main/assets/index.html` 再 Build 一次即可。

# 給 Windows 上 AI 助理的任務：{{APP_NAME}} 的 Windows 實機驗收，以及打包 .exe

使用者會在 Windows 電腦上開這個資料夾。請直接照下面的步驟執行，不只提出計畫。使用者偏好 {{USER_LANGUAGE}}。

## 背景

- {{APP_NAME}} 是在 macOS 上開發的 PySide6 桌面工具：{{ONE_LINE_DESCRIPTION}}
- 這個資料夾是在 Mac 上組裝的可攜版，內附 python.org 的免安裝 Python 與 PySide6-Essentials。
  **在你執行之前，它從未在 Windows 實機上跑過。**
- 原始碼主版本在使用者的 Mac 上。

## 規則

1. **不要修改 `app\{{PKG}}\` 裡的程式碼。** 主版本在 Mac，這裡改了會跟主版本分歧。發現程式問題時寫進回報，
   使用者會帶回 Mac 修正並重新打包。打包流程需要的檔案（例如建置腳本）可以在這個資料夾裡新增。
2. 安裝任何東西前，先告訴使用者要裝什麼、從哪裡下載（python.org、PyPI，都是免費的），等使用者同意再裝。
3. 據實回報：沒有實際執行過的項目不能寫通過；要區分「自動化腳本送出的 Qt 模擬事件」和「使用者用實體滑鼠操作」。
4. 量測數據或私人資料不能放進要分享的 zip，也不能上傳到任何地方。

## 0. 準備資料

請使用者把這些資料檔複製到 Windows：{{DATA_FILES}}。
放在**名稱結尾沒有空白**的資料夾，例如 `%USERPROFILE%\Desktop\{{APP_FILE}}_data\`（Windows 不允許資料夾名稱以空白結尾）。

## 1. 可攜版能不能啟動（一定要做）

1. 雙擊 `{{APP_FILE}}.bat`；視窗沒出現的話改執行 `{{APP_FILE}}_debug.bat`，並查看使用者資料夾內的錯誤記錄檔。
2. 雙擊 `Create_Desktop_Shortcut.bat`，確認桌面和開始功能表出現有圖示的「{{APP_NAME}}」捷徑，而且雙擊捷徑能開啟程式。
3. 確認標題列和工作列顯示 {{APP_NAME}} 的圖示，而不是 Python 的圖示。

## 2. 自動化驗收（真實資料，Windows 真實視窗）

可攜版的 Python 為了縮小體積拿掉了 QtTest，所以要另外建一個環境（第 4 步打包也會用到）：

```bat
py -3.13 -m venv build_venv
build_venv\Scripts\python -m pip install PySide6-Essentials=={{QT_VER}} {{EXTRA_PIP}} pyinstaller
set APP_DATA_DIR=%USERPROFILE%\Desktop\{{APP_FILE}}_data
build_venv\Scripts\python qa\gui_qa.py --out qa_out\gui --shots qa_out\shots --log qa_out\gui_qa_windows_log.json
```

- 如果電腦沒有 Python 3.13，先徵得使用者同意，再從 python.org 安裝（勾選「Add python.exe to PATH」）。
- macOS 上的參考結果：{{MAC_QA_RESULT}}。任何一項失敗都記下完整訊息，並判斷是 Windows 特有的行為（例如 DPI 造成的像素誤差）還是程式問題。
- 檢查 `qa_out\shots\*.png`：中文不能是方塊字，按鈕和數值不能被截斷；記下目前的顯示比例（100%、125%、150%）。

## 3. 請使用者用實體滑鼠操作

請使用者照 `README_Windows.txt` 第五節操作一次，並記錄他們的回報（順不順、有沒有異常）。

## 4. 打包成 .exe（有圖示，雙擊就開）

```bat
build_venv\Scripts\pyinstaller --noconfirm --windowed --name "{{APP_NAME}}" --icon {{APP_FILE}}.ico ^
  --paths app --add-data "app\{{PKG}}\assets;{{PKG}}\assets" entry.py
"dist\{{APP_NAME}}\{{APP_NAME}}.exe" --selftest qa_out\exe_selftest.json
```

- 產物在 `dist\{{APP_NAME}}\`（onedir 模式，啟動比 onefile 快）。self-test 的 JSON 應該顯示 `"frozen": true, "passed": true`。
- 用實際操作確認：雙擊 exe 能開、圖示正確、能讀真實資料，並做一次匯出。
- 把 `dist\{{APP_NAME}}` 壓縮成 `{{APP_FILE}}_Windows_exe.zip`，附上 `README_Windows.txt`，不能放任何量測數據。
- 如果 SmartScreen 或 Defender 擋下，記錄是什麼提示（exe 沒有數位簽章，第一次執行跳出警告是正常的）。

## 5. 回報：寫成這個資料夾裡的 `WINDOWS_REPORT.md`

- Windows 版本、顯示比例、解析度、Python 版本。
- 第 1–4 步各項：通過、失敗或未做，附上證據（命令輸出摘要、截圖路徑、log 檔路徑）。
- 發現的程式問題：重現步驟、截圖、錯誤訊息、你認為的原因（只描述，不要修改 `app\{{PKG}}`）。
- 產出的檔案：`{{APP_FILE}}_Windows_exe.zip`、`qa_out\`。

使用者會把 `WINDOWS_REPORT.md` 和截圖帶回 Mac，交給原本的 AI 助理處理。

{{APP_NAME}}（Windows 可攜版）
=============================

{{ONE_LINE_DESCRIPTION}}
所有計算都在這台電腦上進行，不需要網路，不會上傳資料。

※ 此套件在 macOS 上組裝。尚未在 Windows 實機驗證前，請依第五節做第一次驗收並回報結果。

一、安裝
1. 若 zip 是從網路或通訊軟體下載：在 zip 上按右鍵 →「內容」→ 勾選「解除封鎖」→ 確定。
2. 右鍵 →「全部解壓縮」到任意資料夾（例如 文件\{{APP_FILE}}_Windows）。不要直接在 zip 裡雙擊。
3. 不需要另外安裝 Python；需要 64 位元 Windows 10 或 11。

二、啟動
- 第一次：雙擊「Create_Desktop_Shortcut.bat」，桌面和開始功能表會出現有圖示的「{{APP_NAME}}」捷徑，之後雙擊捷徑即可。
  （資料夾搬到別處後請再執行一次。）
- 也可以直接雙擊「{{APP_FILE}}.bat」。
- 若出現「Windows 已保護您的電腦」：按「其他資訊」→「仍要執行」。
- 視窗沒出現：改雙擊「{{APP_FILE}}_debug.bat」看錯誤訊息並截圖；使用者資料夾內也會有錯誤記錄檔。

三、操作
{{USAGE_STEPS}}

四、資料夾內容
{{APP_FILE}}.bat / {{APP_FILE}}_debug.bat   啟動
Create_Desktop_Shortcut.bat               建立有圖示的桌面／開始功能表捷徑
{{APP_FILE}}.ico                          程式圖示
WINDOWS_AGENT_TASK.md                     給 Windows 上 AI 助理（Claude Code、Codex 等）的驗收與 .exe 打包任務
qa\                                       自動化驗收腳本
entry.py                                  打包 .exe 用的進入點
python\                                   內附的 Python（python.org 官方免安裝版）與套件
app\                                      程式
examples\                                 合成示範資料（不是量測數據）

五、Windows 第一次驗收（請回報）
1. 雙擊捷徑或 .bat，視窗能開啟，中文正常顯示（非方塊字）。
2. 視窗標題列與工作列顯示 {{APP_NAME}} 圖示。
3. {{ACCEPTANCE_STEPS}}
4. 在 125%／150% 顯示比例下檢查文字與按鈕未被截斷。
5. 資料夾名稱不要以空白結尾（Windows 不允許）。

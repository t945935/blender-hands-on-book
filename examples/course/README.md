# 課程檢查點與唯讀報告

這份配套只含獨立練習場景與工具，不含章節內文。檔案以 Blender **5.2.2 LTS** 背景模式建立，並由另一個 Blender 程序重新開啟驗收；PNG 是程式生成的成果參考，**不是 GUI 操作截圖，也不是真人試讀證據**。

## 檔案用途

| 檔案 | 內容與界線 |
|---|---|
| `checkpoints/board-applied.blend` | `Board_Test` 尺寸為 0.36 × 0.24 × 0.006 m、Location Z = 0.003 m，Scale 三軸皆為 1。這是套用縮放後的獨立底板練習，不是完成的托盤。 |
| `checkpoints/tray-surface.blend` | `Tray` 原始網格為 8 頂點、12 邊、5 面；寬 0.36 m、深 0.24 m，底面 Z = 0.006 m、上緣 Z = 0.08 m，物件 Location 為零。底面法線向上、側壁朝內，尚無厚度，不能視為可製造實體。 |
| `checkpoints/tray-modifiers.blend` | 保留 Solidify → Bevel；厚度 0.006 m、Offset −1、Even Thickness 與 Fill Rim 開啟；Bevel 寬度 0.0015 m、Segments 3。重新載入後，求值網格通過閉合流形與正有號體積檢查，但不代表已通過加工、列印或承重驗證。 |
| `checkpoints/dividers-nodes.blend` | 獨立 `GN_Dividers` 場景。Mesh Line Count 3、Start Location (−0.12, 0, 0)、Offset (0.12, 0, 0)；Cube Size (0.005, 0.234, 0.052) m → Instance on Points → Realize Instances → Group Output。沒有既有托盤與隔板，不保證可直接塞入其他佈景。 |
| 同名 `.png` | 每個檢查點各有一張 960 × 720 參考圖；相機與燈光在 `Preview_Studio` 集合。預覽材質只是方便辨識，不能以顏色判斷法線方向。 |
| `scripts/inspect_scene.py` | 只印出 JSON 報告：Blender 版本、目前場景，以及物件名稱、型別、Location、Scale、所屬集合。不改名、不選取、不儲存、不寫檔，也不啟動外部程式。Location 與 Scale 是物件本地變換，不是求值後世界邊界。 |
| `checkpoints/generation.json` | 產生工具的版本、檔案清單及渲染設定；這份清單本身不是獨立驗收結果。 |

本配套的 `.blend` 與 PNG 放在 `checkpoints/` 子資料夾。場景不依賴外部貼圖；渲染輸出使用相對路徑，搬移 `.blend` 後會以其所在資料夾為準。

## 安全使用

- 先用 **Save As／另存新檔** 建立自己的副本；不要覆寫檢查點、舊原型或自己的作業。
- 開啟場景不需要開啟「Auto Run Python Scripts」。不要因為下載了 `.blend` 就信任其中的程式。
- 唯讀工具仍應先讀過原始碼再執行。它只查詢目前場景，不會遍歷其他檔案或上傳資料，也不需要額外 Python 套件或 WSL。
- 背景程序輸出會夾帶 Blender 本身的版本、讀檔及結束訊息；JSON 物件是腳本報告，但整段終端文字不一定是合法 JSON 檔。
- 相機、燈光也會列入物件報告；不要把報告中的物件總數當作網格數。
- 零厚度開口表面的有號體積沒有封閉實體意義；先確認閉合流形，再討論體積。

## 選用：Windows PowerShell 執行唯讀報告

在本資料夾（`examples/course`）開啟 PowerShell，依安裝位置調整 `$Blender`。不必安裝命令列 Python。

```powershell
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$Scene = (Resolve-Path '.\checkpoints\tray-modifiers.blend').Path
$Script = (Resolve-Path '.\scripts\inspect_scene.py').Path
& $Blender --background --factory-startup --disable-autoexec $Scene --python-exit-code 1 --python $Script
if ($LASTEXITCODE -ne 0) { throw "Blender 檢查失敗，退出碼 $LASTEXITCODE" }
```

也可在 Blender 的 Text Editor 開啟 `inspect_scene.py` 並執行；報告印在主控台，不會插入場景或建立文字檔。

## 檢查點與驗證的界線

這些檢查點由作者建置工具產生；生成器不屬於本次讀者配套，核心課程與唯讀報告均不需要它。`checkpoints/generation.json` 記錄生成版本與設定；請配合自己的GUI操作和回載檢查，不要僅憑生成清單認定作業已通過。

產生與驗收屬自動化證據；不能將這些檔案描述為每個 GUI 步驟、全部故障分支或製造條件都已實測。

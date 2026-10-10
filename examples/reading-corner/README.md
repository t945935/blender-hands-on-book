# 桌面閱讀角落配套

這是檔案使用說明，不是書中章節內文。初學讀者只需開啟 `chapter01-start.blend` 並另存副本，不必執行下列程式。

## 檔案

- `chapter01-start.blend`：第1章起始場景。
- `reading-corner.blend`：完整原型場景。
- `reading-corner.glb`：七個模型的 GLB，已套用修改器後匯出。
- `hero.png`、`front.png`、`top.png`：原型參考渲染。
- `scene.py`：選用的建置與驗證程式，須由 Blender 內建 Python 執行。

物件名稱保留英文。起始 `Accent_Block` 位置是 `(0.15, -0.205, 0)` 公尺，縮放是 `(1, 1, 1)`；原點在底面中央。

## 選用：重新建置原型

以下為 Windows PowerShell 命令。先切換到解壓後的 `examples/reading-corner` 資料夾，將 Blender 路徑改成實際安裝位置。關閉其他未保存的操作不會由此命令代勞；這些命令使用獨立背景程序。

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --threads 8 --python-exit-code 1 --python .\scene.py -- build .\generated
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --threads 8 --python-exit-code 1 --python .\scene.py -- native .\generated
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --threads 8 --python-exit-code 1 --python .\scene.py -- glb .\generated
```

每行完成後查看 `$LASTEXITCODE`，為 `0` 才繼續下一行。`build` 會渲染三張圖片，可能需要等待；輸出資料夾必須不存在或為空，否則程式拒絕建置，避免覆寫練習。

`native` 讀取建置出的兩個 BLEND，在記憶體中驗證物件、托盤幾何與變形安全性，不把測試變形另存；會寫入 `native-check.json`。`glb` 需要 `build` 產生的 `export-reference.json`，回匯 GLB 並核對世界座標邊界，寫入 `glb-check.json`。這些是資料檢查，不代表 GUI 跟做、跨平台或真人試讀驗收。

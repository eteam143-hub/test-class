# 任天堂瑪利歐兄弟啟動器

這是獨立遊戲啟動專案。未放 ROM 時會啟動內附、可直接遊玩的原創「水管工跳躍冒險」；若放入合法自備的瑪利歐 NES ROM，則會以 Mednafen 執行該 ROM。專案不包含遊戲 ROM。

## 使用方式

1. 將你合法擁有並自行備份的 ROM 放到 `roms/`，例如：

   - `Super Mario Bros.nes`
   - `Super Mario Bros. (World).nes`
   - `Mario Bros.nes`

2. 執行：

   ```bash
   cd 0922-1
   ./play_mario.sh
   ```

未放 ROM 時的原創遊戲按鍵：

- `←` / `→` 或 `A` / `D`：移動
- `Space` / `X` / `↑`：跳躍
- `ESC`：結束遊戲

## 按鍵

| NES 按鍵 | 鍵盤 |
| --- | --- |
| 方向鍵 | `↑` `↓` `←` `→` |
| B（跑步／發射） | `Z` |
| A（跳躍） | `X` |
| START | `Enter` |
| SELECT | `Tab` |
| 結束遊戲 | `ESC` |

首次使用若沒有模擬器：

```bash
sudo apt install mednafen
```

# NES 任天堂復古遊戲機 (0922)

用 Raspberry Pi + Python(pygame) + Mednafen 模擬器玩任天堂紅白機(NES/FC)遊戲。

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `play_nes.py` | 主程式:pygame 遊戲選單,挑選 ROM 後啟動模擬器 |
| `play_nes.sh` | 執行檔:一鍵啟動主程式 |
| `roms/` | 放置 `.nes` 遊戲檔的資料夾 |
| `mednafen.cfg` | NES 按鍵與畫面設定(啟動時自動套用) |

## 開始使用

```bash
cd 0922
./play_nes.sh
```

## 操作方式

選單畫面:

- `↑` / `↓` 或 `W` / `S`:選擇遊戲或「離開遊戲、回到桌面」
- `Enter` / `Space`:開始所選遊戲，或確認離開
- `ESC` / `Q`:隨時離開選單、回到桌面

遊戲中:

- `ESC`:結束遊戲、回到遊戲選單（已設定，不必按預設的 `F12`）
- 回到桌面:在選單再按一次 `ESC`

貪食蛇:

- `↑` `↓` `←` `→` 或 `W` `A` `S` `D`:移動
- `Enter` / `Space`:暫停或繼續
- 遊戲結束時按 `Enter` / `Space` / `R`:重新開始
- `ESC`:回到遊戲選單

魚兒墜落:

- `←` `→` 或 `A` `D`:移動小船接住魚兒
- `Enter` / `Space`:暫停或繼續
- 遊戲結束時按 `Enter` / `Space` / `R`:重新開始
- `ESC`:回到遊戲選單

離開軟體:

- 在選單按 `ESC`,程式的 pygame 視窗關閉後即回到桌面

遊戲中 NES 手把按鍵對應:

| NES 按鍵 | 鍵盤 |
|----------|------|
| 方向鍵 | `↑` `↓` `←` `→` |
| B | `Z` |
| A | `X` |
| SELECT | `Tab` |
| START | `Enter` |

也支援 USB 遊戲手把。

## 加入遊戲

把任天堂紅白機(FC/NES)遊戲的 ROM 檔(`.nes`)複製到 `roms/` 資料夾即可。

## 安裝需求(僅第一次)

```bash
sudo apt install mednafen        # NES 模擬器
uv sync                          # 安裝 Python 套件(pygame)
```

## 疑難排解

- **按 Enter 遊戲開不起來**:現在啟動失敗時,紅字錯誤訊息會直接顯示在畫面上,
  詳細紀錄在 `launcher.log`。把它內容(或畫面紅字)回報即可。
- **透過 VNC/遠端連線玩**:VNC 下若畫面黑色或卡住,先在終端機執行下方指令
  改用「視窗模式」啟動模擬器(較不會和 VNC 搶畫面):

  ```bash
  NES_WINDOW=1 ./play_nes.sh
  ```

- **鍵盤 Enter 沒反應**:有些鍵盤/VNC 用戶端送的是小鍵盤 Enter,目前已同時支援。

目前 `roms/` 內附 8 個免費的 homebrew(自製)遊戲做為測試:
`Alter Ego`、`Columns`、`D-Pad Hero`、`Fishfall`、`Geminim`、
`Hoppin Mad`、`Nanaca-Crash!!`、`Snake`。
將自己的正版卡帶 ROM 放入後即可遊玩更多遊戲。

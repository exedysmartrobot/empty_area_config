# Frame Designer — Flask 版

ロボットのマップ上に「空きエリア判定用の枠（ROBOT/LiDAR）」を配置・編集し、
`frame_config.yaml` として書き出すツール。ロボットAPIと連携して、マップ画像・
現在地・登録ルートをそのまま画面に重ねて確認しながら作業できる。

## 構成

```
empty_area_config_flask/
├── server.py               # Flask本体（画面配信 + ロボットAPI中継）
├── app_client.py           # ロボットのカスタムアプリAPIを叩く共通クライアント
├── common.py                # load_json などの共通ユーティリティ
├── module/                  # 暗号化(encrypt/decrypt)などロボット通信用モジュール
├── auth_config.json         # ロボットAPI認証情報（UserID/Password/OPKey/TenantCD）
├── .env                     # ROBOT_ID / CUSTOMER_HOST / CUSTOMER_URL
├── templates/index.html     # 画面本体（UI・描画ロジックは全てここ）
├── static/                  # 静的ファイル置き場
└── configs/                 # 設定ファイルの保存先（自動生成）
```

## 事前準備

1. `.env` に対象ロボットの ID とゲートウェイ先を設定する。

   ```
   ROBOT_ID=SR08_2507040001
   CUSTOMER_HOST=https://alb-cstm-ctn.exedy-robo.com
   CUSTOMER_URL=/ForwardCustom
   ```

2. `auth_config.json` にロボットAPIの認証情報（UserID/Password/OPKey/TenantCD）
   が入っていることを確認する。

## 起動

```bash
pip install flask requests python-dotenv pycryptodome
python server.py
```

ブラウザで http://localhost:5000 を開く。起動すると自動で

- マップ画像の取得（`get_map`）
- ロボット現在地の取得（`get_pose`）
- 登録ルート一覧の取得（`get_map_id` → ルート一覧API）

が実行され、マップ上にすべて重ねて表示される。

## 使い方

### 画面上部（ヘッダー）

- **APIから取得**: マップ画像を再取得
- **現在地を更新**: ロボットの現在位置（矢印＝向き）を再取得してマップに表示
- **解像度 (m/px)**: 使用中マップの解像度。枠のサイズをm指定するときの換算に使う（デフォルト0.05）
- **全体表示 / 書き出す**: 表示のフィット / `frame_config.yaml`(or JSON) のダウンロード

### 右パネルのタブ

1. **生成**: ROBOT/LiDARそれぞれの「基準タイル」を描き、num_x×num_yで一括生成する。
   - 基準タイルは「上辺2点」「左辺2点」「四隅」のいずれかでキャンバス上に描くか、
     幅(m)/高さ(m)欄に数値を入れて直接サイズ指定して作ることもできる（解像度をもとにpx換算）。
2. **一覧**: 生成済みの枠一覧。並び替え・位置順の自動採番など。
3. **編集**: 選択した枠1つ（複数選択も可）を、幅・高さ・角度（pxまたはm）や
   四隅の座標を直接編集。整列・複製・回転・拡縮なども可能。
4. **ルート**: ロボットに登録されているルート一覧。チェックを入れたルートだけ
   マップ上に経路線・各waypoint・終点の向きが表示される。

### 枠のサイズをm指定する

「編集」タブの選択中の枠、または「生成」タブの基準タイルにある
幅(m)/高さ(m)欄に数値を入力すると、ヘッダーの解像度をもとにpx換算して
その値ちょうどのサイズに整形される（位置・角度は変わらない）。
上下キーでの増減幅も解像度に合わせてある（デフォルト0.05m刻み）。

## API疎通確認

```js
fetch('/api/ping').then(r => r.json()).then(console.log)
// → {ok: true, message: "flask is running"}
```

## サーバー側エンドポイント

| エンドポイント | 内容 |
| --- | --- |
| `GET /api/robot_map` | `main_api_client(ROBOT_ID, "get_map", {})` の結果を中継 |
| `GET /api/robot_pose` | `main_api_client(ROBOT_ID, "get_pose", {})` の結果を中継 |
| `GET /api/route_list` | `get_map_id` でmap_idを取得し、登録ルート一覧を中継 |

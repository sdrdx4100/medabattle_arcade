# Medabattle Arcade Prototype

このリポジトリはArcadeライブラリを用いたメダロット風ATBシミュレーションRPGのプロトタイプです。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 実行方法

```bash
python main.py
```

## 操作方法

* 方向キー: 選択/移動
* Enter/Space: 決定
* Esc: キャンセル/終了
* Tab/M: メニュー開閉

起動するとタイトル→セーブスロット→メインメニュー→ストーリー→ATBバトルと進行する最小縦貫フローを体験できます。

このプロジェクトは学習目的の簡易実装です。

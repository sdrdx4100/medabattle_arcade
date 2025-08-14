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

## シャトルランバトル

`python main.py` で起動すると、3vs3 のシャトルラン式ATBバトルが開始されます。
ATBゲージが満タンになった味方にはコマンドメニューが表示され、
方向キーで項目選択し Enter/Space で決定します。

コマンドは以下の二つです。

* **たたかう**: 中央まで走って攻撃します。
* **待機**: ATBゲージをリセットして待機します。

攻撃結果や勝敗は画面下部のメッセージウィンドウに表示されます。
どちらかが全滅するとバトル終了です。

このプロジェクトは学習目的の簡易実装です。

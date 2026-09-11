# カス高 キャラクター名鑑

オリジナルストーリー「マジカルカース帝国国立高等学校（カス高）」のキャラクター紹介サイトです。

## 今後のキャラクター追加

キャラクターごとのHTMLや中央データの手編集は不要です。1人分を `characters-data/{id}/` の3ファイルにまとめ、公開時に一覧データを自動生成します。

### ChatGPTに追加を頼む場合

次の3点を渡せば追加できます。

1. キャラクター設定
2. AI立ち絵
3. 元手書き資料

画像の形式や大きさは問いません。追加ツールがWebPへの変換、縮小、命名、並び順の設定、表示用データの生成をまとめて行います。今後GitHubへ追加するのは、新キャラクターのフォルダ内にできる3ファイルだけです。

### 手元で追加する場合

初回だけ画像変換用ライブラリを入れます。

    python -m pip install -r tools/requirements.txt

`tools/character-template.json` をコピーして設定を書き、次を実行します。

    python tools/add-character.py --record new-character.json --portrait new-character-ai.png --original new-character-original.png

これだけで `characters-data/{id}/` に次の3ファイルが作られます。

- `profile.json`: キャラクター設定
- `portrait.webp`: AI立ち絵
- `original.webp`: 元手書き資料

同時に次の処理も完了します。

- 画像を表示品質を保ったWebPへ変換
- 大きすぎる画像だけ縦横比を保って縮小
- 1人分を独立したフォルダへ保存
- 表示用の `data/characters.json` を自動生成
- トップ一覧と共通詳細ページへ自動反映

同じ `id` の二重登録や画像の上書きは自動で止めます。

## 主なファイル

- `index.html`: キャラクター一覧
- `character.html?id={id}`: 全キャラクター共通の詳細ページ
- `characters-data/{id}/`: 1人分の設定と画像2枚
- `data/characters.json`: 公開時に自動生成される表示用データ
- `app.js`: 一覧・詳細ページの自動生成
- `styles.css`: 全ページ共通CSS
- `assets/`: 立ち絵と元手書き資料
- `tools/add-character.py`: 画像変換と登録をまとめて行う追加ツール
- `tools/build-catalog.py`: 各フォルダから表示用データを生成
- `tools/validate-catalog.py`: データと画像参照の自動検査
- `tools/character-template.json`: 新キャラクター用ひな形

旧URLの `characters/plus.html` などは、新しい共通詳細ページへ自動転送されます。
公開前に表示用データの生成と検査が自動実行されるため、設定漏れや画像不足がある状態では更新されません。既存キャラクターを編集するときも、その人物のフォルダだけを変更します。

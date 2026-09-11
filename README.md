# カス高 キャラクター名鑑

オリジナルストーリー「マジカルカース帝国国立高等学校（カス高）」のキャラクター紹介サイトです。

## 今後のキャラクター追加

キャラクターごとのHTMLは作りません。一覧と詳細ページは `data/characters.json` から自動生成されます。

### ChatGPTに追加を頼む場合

次の3点を渡せば追加できます。

1. キャラクター設定
2. AI立ち絵
3. 元手書き資料

画像の形式や大きさは問いません。追加ツールがWebPへの変換、適切な縮小、ファイル名の統一、名鑑データへの登録をまとめて行います。

### 手元で追加する場合

初回だけ画像変換用ライブラリを入れます。

    python -m pip install -r tools/requirements.txt

`tools/character-template.json` をコピーして設定を書き、次を実行します。

    python tools/add-character.py --record new-character.json --portrait new-character-ai.png --original new-character-original.png

これだけで次の処理が完了します。

- 画像を表示品質を保ったWebPへ変換
- 大きすぎる画像だけ縦横比を保って縮小
- `assets/{id}-ai.webp` と `assets/{id}-original.webp` に保存
- `data/characters.json` へキャラクターを追加
- トップ一覧と共通詳細ページへ自動反映

同じ `id` の二重登録や画像の上書きは自動で止めます。

## 主なファイル

- `index.html`: キャラクター一覧
- `character.html?id={id}`: 全キャラクター共通の詳細ページ
- `data/characters.json`: キャラクター設定
- `app.js`: 一覧・詳細ページの自動生成
- `styles.css`: 全ページ共通CSS
- `assets/`: 立ち絵と元手書き資料
- `tools/add-character.py`: 画像変換と登録をまとめて行う追加ツール
- `tools/validate-catalog.py`: データと画像参照の自動検査
- `tools/character-template.json`: 新キャラクター用ひな形

旧URLの `characters/plus.html` などは、新しい共通詳細ページへ自動転送されます。
公開前にも自動検査されるため、設定漏れや画像名の間違いがある状態では更新されません。

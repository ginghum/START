# カス校名鑑STORY

公開入口: `story/index.html`。通常名鑑と共通の `app.js`、`styles.css`、立ち絵を利用し、人物データは独立した `characters.json` から読み込みます。

第2章第24話まで（第1章・おまけ3を含む）。会話・行動・回想で登場した49人を掲載しています。名前が言及されただけの人物は含めません。紹介文・セリフ・初登場話・登場話リンクは本文に基づきます。基本プロフィールと画像は通常名鑑を参照しています。

プラスはGrade 2、ヒカルとコバルはGrade 4。通常名鑑の将来の昇格は同期しません。本文で未披露の能力や形態、裏設定も持ち込みません。人物の事実と、Xなどが伝えた情報や未確定の推測を区別してください。

続話で追加・更新するときは、最新の `ginghum/cursehighschool-` の本文を確認し、このJSONの紹介・登場話・Gradeを編集します。通常名鑑用のビルドによって、このJSONが上書きされることはありません。`source.json` の対象範囲と本文のcommit/hash、両HTMLの収録範囲表示も更新してください。

確認: `node --check app.js`、`python tools/build-catalog.py`、`python tools/validate-catalog.py`、`python tools/validate-story-catalog.py`。

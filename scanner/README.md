# 反射型XSS脆弱性診断スクリプト + PHPやられアプリ

チームB計画書（修正版）の①〜⑨の必須機能に対応した実装です。

```
project/
├── htdocs/            やられアプリ（PHP）。XAMPP の htdocs 配下に置く
│   ├── index.php      ページ一覧ポータル
│   └── *.php          各コンテキスト×対策あり/なしのテストページ
└── scanner/           診断スクリプト本体（Python）
    ├── xss_scanner.py
    ├── payloads.json
    ├── requirements.txt
    └── modules/
        ├── payload_manager.py   ① ペイロードリストの管理
        ├── requester.py         ③④ 通信処理・ベースライン/反射チェック送信
        ├── context_detector.py  ⑤ 反射コンテキストの判定
        ├── escape_checker.py    ⑦ エスケープ判定
        ├── exploit_checker.py   ⑧ 実行可能性の判定
        ├── reporter.py          ⑨ 結果出力（CSV・サマリー）
        ├── models.py            判定結果のデータ構造
        └── logger_config.py     通信ログ記録
```

## 1. やられアプリ（PHP / XAMPP）のセットアップ

1. `htdocs/` フォルダの中身を XAMPP の `htdocs` フォルダ（例: `C:\xampp\htdocs\xss-lab\` や
   `/Applications/XAMPP/htdocs/xss-lab/`）にコピーする。
2. XAMPP コントロールパネルで Apache を起動する。
3. ブラウザで `http://localhost/xss-lab/index.php` にアクセスし、一覧からページを確認する。

ローカルで素早く試したいだけの場合は、XAMPPのApacheの代わりにPHP単体のビルトインサーバーでも動きます。

```bash
cd htdocs
php -S localhost:8000
# ブラウザで http://localhost:8000/index.php
```

### 用意したページ（コンテキスト × 対策の有無）

| コンテキスト | 未対策 | 対策不十分 | 対策済み |
| :--- | :--- | :--- | :--- |
| タグの間 | `tag_vuln.php` | - | `tag_safe.php` |
| 属性値の中(") | `attr_dq_vuln.php` | `attr_dq_partial.php`（`ENT_NOQUOTES`） | `attr_dq_safe.php` |
| 属性値の中(') | `attr_sq_vuln.php` | `attr_sq_partial.php`（`ENT_COMPAT`） | `attr_sq_safe.php` |
| scriptの中 | `script_vuln.php` | - | `script_safe.php`（`json_encode`） |
| URL属性 | `url_attr_vuln.php` | - | `url_attr_safe.php`（スキーム検証） |
| POST | `post_vuln.php`（未対策） | - | - |
| 反射なし | `no_reflect.php` | - | - |

パラメータ名はすべて `keyword`（POSTページのみ `comment`、URL属性ページのみ `link`）です。

## 2. 診断スクリプトのセットアップ

```bash
cd scanner
pip install -r requirements.txt
```

## 3. 使い方

```bash
# 未対策ページ（タグの間）
python xss_scanner.py --url http://localhost/xss-lab/tag_vuln.php --param keyword

# POSTフォーム
python xss_scanner.py --url http://localhost/xss-lab/post_vuln.php --param comment --method POST

# localhost以外を対象にする場合は許可済みであることの確認が入ります（--yes で省略可）
python xss_scanner.py --url http://localhost/xss-lab/attr_dq_vuln.php --param keyword --output result.csv
```

実行すると、
1. ランダムな識別子を送って反射位置を特定し、
2. 反射位置ごとにHTML上のコンテキスト（タグの間/属性値の中/scriptの中/URL属性）を判定し、
3. そのコンテキストに合うペイロードだけを `payloads.json` から選んで送信し、
4. 特殊文字の変換有無（エスケープ判定）と、HTMLパーサによる実行可能性の判定を行い、
5. `result.csv`（既定）に判定理由付きで1行ずつ出力し、画面に件数サマリーを表示します。

### result.csv の列

`url, param, method, context, payload, unescaped_chars, verdict, reason`

`verdict` は次の4区分です。

- **反射なし**：識別子がレスポンスに出現しない
- **反射型XSSの疑いあり**：必要な文字が未変換で、かつ実行されうる構造が成立
- **対策済み**：必要な文字が変換/除去され、実行されうる構造が成立しない
- **要手動確認**：コメント内・タグ名/属性名などの反射、または自動判定できなかった場合

## 4. 利用上の注意

- 自分が管理する環境（localhost / XAMPP）でのみ使用してください。
- 検出できるのは反射型XSSのみです。保存型XSS・DOM型XSSは対象外です。
- 「対策済み」は安全性の保証ではなく、本スクリプトの判定基準による一次チェックの結果です。

<?php
// やられアプリ ポータル（反射型XSS診断スキャナ 動作確認用）
// すべてローカル環境専用。わざと脆弱なページと対策済みページを並べている。
$pages = [
    ["name" => "タグの間・未対策", "path" => "tag_vuln.php?keyword=test", "desc" => "<h1>keyword</h1> にそのまま出力"],
    ["name" => "タグの間・対策済み", "path" => "tag_safe.php?keyword=test", "desc" => "htmlspecialchars(ENT_QUOTES) 適用"],
    ["name" => "属性値(\")・未対策", "path" => "attr_dq_vuln.php?keyword=test", "desc" => "value=\"keyword\" にそのまま出力"],
    ["name" => "属性値(\")・対策不十分", "path" => "attr_dq_partial.php?keyword=test", "desc" => "ENT_NOQUOTES のため \" が未変換"],
    ["name" => "属性値(\")・対策済み", "path" => "attr_dq_safe.php?keyword=test", "desc" => "ENT_QUOTES で \" も変換"],
    ["name" => "属性値(')・未対策", "path" => "attr_sq_vuln.php?keyword=test", "desc" => "value='keyword' にそのまま出力"],
    ["name" => "属性値(')・対策不十分", "path" => "attr_sq_partial.php?keyword=test", "desc" => "ENT_COMPAT のため ' が未変換"],
    ["name" => "属性値(')・対策済み", "path" => "attr_sq_safe.php?keyword=test", "desc" => "ENT_QUOTES で ' も変換"],
    ["name" => "scriptの中・未対策", "path" => "script_vuln.php?keyword=test", "desc" => "JS文字列リテラルにそのまま出力"],
    ["name" => "scriptの中・対策済み", "path" => "script_safe.php?keyword=test", "desc" => "json_encode でエスケープ"],
    ["name" => "URL属性・未対策", "path" => "url_attr_vuln.php?link=test", "desc" => "href=\"link\" にそのまま出力"],
    ["name" => "URL属性・対策済み", "path" => "url_attr_safe.php?link=test", "desc" => "スキームをホワイトリストで検証"],
    ["name" => "POST・未対策", "path" => "post_vuln.php", "desc" => "comment を POST で受け取り反射"],
    ["name" => "反射なし", "path" => "no_reflect.php?keyword=test", "desc" => "入力値を画面に出さない"],
];
?>
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>やられアプリ ポータル (PHP / XAMPP)</title>
<style>
body { font-family: sans-serif; padding: 24px; background: #fafafa; }
table { border-collapse: collapse; width: 100%; max-width: 900px; }
th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
th { background: #1a3c6e; color: #fff; }
tr:nth-child(even) { background: #f0f0f0; }
code { background: #eee; padding: 2px 4px; }
</style>
</head>
<body>
<h1>やられアプリ ポータル</h1>
<p>反射型XSS診断スキャナ（xss_scanner.py）の動作確認・精度調整用のテストページ一覧です。<br>
自分が管理するローカル環境（XAMPP / localhost）以外では使用しないでください。</p>
<table>
<tr><th>ページ</th><th>リンク</th><th>内容</th></tr>
<?php foreach ($pages as $p): ?>
<tr>
    <td><?= htmlspecialchars($p["name"], ENT_QUOTES, "UTF-8") ?></td>
    <td><a href="<?= htmlspecialchars($p["path"], ENT_QUOTES, "UTF-8") ?>"><code><?= htmlspecialchars($p["path"], ENT_QUOTES, "UTF-8") ?></code></a></td>
    <td><?= htmlspecialchars($p["desc"], ENT_QUOTES, "UTF-8") ?></td>
</tr>
<?php endforeach; ?>
</table>
</body>
</html>

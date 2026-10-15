<?php
// 入力値を画面に一切出さないページ（「反射なし」判定の確認用）
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
$count = strlen($keyword); // ログにのみ使う想定で、画面には出さない
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>検索結果</title></head>
<body>
<h1>検索結果</h1>
<p>一致する結果は見つかりませんでした。</p>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

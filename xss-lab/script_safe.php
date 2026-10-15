<?php
// 【対策済み】json_encode で文字列リテラルとして安全にエスケープする
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
$safe = json_encode($keyword, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP);
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>script内対策済み</title></head>
<body>
<h1>検索ログ送信</h1>
<script>
var q = <?= $safe ?>;
console.log('search:', q);
</script>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

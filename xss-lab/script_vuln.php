<?php
// 【未対策】scriptタグ内の文字列リテラルにそのまま出力する
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>script内未対策</title></head>
<body>
<h1>検索ログ送信</h1>
<script>
var q = '<?= $keyword ?>';
console.log('search:', q);
</script>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

<?php
// 【対策不十分】ENT_COMPAT を指定しているため ' が変換されない
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
$partial = htmlspecialchars($keyword, ENT_COMPAT, "UTF-8");
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>属性値(SQ)対策不十分</title></head>
<body>
<h1>再検索</h1>
<form action="attr_sq_partial.php" method="GET">
<input type='text' name='keyword' value='<?= $partial ?>' size='50'>
<button type="submit">検索</button>
</form>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

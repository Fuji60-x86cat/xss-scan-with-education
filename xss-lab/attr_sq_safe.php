<?php
// 【対策済み】ENT_QUOTES で ' も変換する
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
$safe = htmlspecialchars($keyword, ENT_QUOTES, "UTF-8");
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>属性値(SQ)対策済み</title></head>
<body>
<h1>再検索</h1>
<form action="attr_sq_safe.php" method="GET">
<input type='text' name='keyword' value='<?= $safe ?>' size='50'>
<button type="submit">検索</button>
</form>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

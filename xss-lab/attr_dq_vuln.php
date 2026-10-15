<?php
// 【未対策】属性値（ダブルクォート）コンテキスト
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>属性値(DQ)未対策</title></head>
<body>
<h1>再検索</h1>
<form action="attr_dq_vuln.php" method="GET">
<input type="text" name="keyword" value="<?= $keyword ?>" size="50">
<button type="submit">検索</button>
</form>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

<?php
// 【対策済み】タグの間コンテキスト：htmlspecialchars(ENT_QUOTES) で変換してから出力
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
$safe = htmlspecialchars($keyword, ENT_QUOTES, "UTF-8");
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title><?= $safe ?> の検索結果</title></head>
<body>
<h1><?= $safe ?> の検索結果</h1>
<p>検索キーワード「<?= $safe ?>」に一致する結果はありませんでした。</p>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

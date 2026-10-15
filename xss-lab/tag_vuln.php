<?php
// 【未対策】タグの間コンテキスト：GETパラメータをそのままHTML本文に出力する
$keyword = isset($_GET["keyword"]) ? $_GET["keyword"] : "";
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title><?= $keyword ?> の検索結果</title></head>
<body>
<h1><?= $keyword ?> の検索結果</h1>
<p>検索キーワード「<?= $keyword ?>」に一致する結果はありませんでした。</p>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

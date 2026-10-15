<?php
// 【対策済み】スキームを http/https のみに制限し、それ以外は無害な値に差し替える
$link = isset($_GET["link"]) ? $_GET["link"] : "";
$scheme = parse_url($link, PHP_URL_SCHEME);
if ($scheme !== null && !in_array(strtolower($scheme), ["http", "https"], true)) {
    $link = "#blocked";
}
$safe = htmlspecialchars($link, ENT_QUOTES, "UTF-8");
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>URL属性対策済み</title></head>
<body>
<h1>関連リンク</h1>
<p><a href="<?= $safe ?>">関連ページへ</a></p>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

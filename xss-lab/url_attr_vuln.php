<?php
// 【未対策】href属性にスキーム検証なしで出力する（javascript: スキームが通る）
$link = isset($_GET["link"]) ? $_GET["link"] : "";
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>URL属性未対策</title></head>
<body>
<h1>関連リンク</h1>
<p><a href="<?= $link ?>">関連ページへ</a></p>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

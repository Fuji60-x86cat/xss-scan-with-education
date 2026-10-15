<?php
// 【未対策】POSTで受け取ったコメントをそのまま出力する
$comment = (isset($_SERVER["REQUEST_METHOD"]) && $_SERVER["REQUEST_METHOD"] === "POST" && isset($_POST["comment"])) ? $_POST["comment"] : "";
?>
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>コメント投稿(POST未対策)</title></head>
<body>
<h1>コメント投稿フォーム</h1>
<form action="post_vuln.php" method="POST">
<textarea name="comment" rows="3" cols="40"></textarea><br>
<button type="submit">投稿</button>
</form>
<hr>
<h3>最新の投稿</h3>
<div><?= $comment !== "" ? $comment : "(投稿はありません)" ?></div>
<p><a href="index.php">← トップへ戻る</a></p>
</body>
</html>

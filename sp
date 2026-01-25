<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Start Page</title>
    <style>
        /* 배경 및 기본 스타일 */
        body {
            background-color: #000000; /* 검정 배경 */
            color: #ffffff; /* 흰색 글자 */
            font-family: 'Malgun Gothic', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        /* 링크 컨테이너 */
        .container {
            text-align: center;
        }

        /* 링크 아이템 스타일 */
        .link-item {
            display: inline-block;
            margin: 15px 25px;
            text-decoration: none;
            color: #aaaaaa; /* 기본 회색 */
            font-size: 2rem;
            font-weight: bold;
            transition: 0.3s;
        }

        /* 마우스를 올렸을 때 효과 */
        .link-item:hover {
            color: #ffffff; /* 마우스 올리면 흰색으로 */
            transform: scale(1.1);
        }
    </style>
</head>
<body>

    <div class="container">
        <a href="https://www.youtube.com/" class="link-item">yt</a>
        <a href="https://namu.wiki/" class="link-item">nm</a>
        
        </div>

</body>
</html>

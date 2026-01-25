#!/bin/bash

# 생성될 파일 이름
OUTPUT="index.html"
INPUT="list.txt"

# HTML 상단 부분 작성
cat <<EOF > $OUTPUT
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Start Page</title>
    <style>
        body {
            background-color: #000000;
            color: #ffffff;
            font-family: 'Malgun Gothic', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container { text-align: center; }
        .link-item {
            display: inline-block;
            margin: 15px 25px;
            text-decoration: none;
            color: #aaaaaa;
            font-size: 2rem;
            font-weight: bold;
            transition: 0.3s;
        }
        .link-item:hover {
            color: #ffffff;
            transform: scale(1.1);
        }
    </style>
</head>
<body>
    <div class="container">
EOF

# list.txt를 읽어서 링크 생성
while read -r name url; do
    # 빈 줄이나 주석(#)은 건너뜀
    [[ -z "$name" || "$name" == "#"* ]] && continue
    echo "        <a href=\"$url\" class=\"link-item\">$name</a>" >> $OUTPUT
done < "$INPUT"

# HTML 하단 부분 마무리
cat <<EOF >> $OUTPUT
    </div>
</body>
</html>
EOF

echo "성공: $OUTPUT 파일이 생성되었습니다."

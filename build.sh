#!/bin/bash

OUTPUT="index.html"
INPUT="list.txt"

cat <<EOF > $OUTPUT
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Dashboard</title>
    <style>
        body {
            background-color: #0f0f0f; /* 깊은 검정 */
            color: #efefef;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            display: grid;
            /* 화면 너비에 따라 자동으로 칸 조절 (최소 120px) */
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 20px;
            width: 90%;
            max-width: 800px;
            padding: 40px;
        }
        .link-item {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80px;
            background-color: #1a1a1a; /* 카드 배경 */
            color: #ffffff;
            text-decoration: none;
            font-size: 1.2rem;
            font-weight: 600;
            border-radius: 12px;
            border: 1px solid #333;
            transition: all 0.2s ease-in-out;
            text-transform: uppercase; /* 대문자로 세련되게 */
        }
        .link-item:hover {
            background-color: #333;
            border-color: #555;
            transform: translateY(-5px); /* 위로 살짝 들림 */
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        @media (max-width: 480px) {
            .container { grid-template-columns: repeat(2, 1fr); } /* 모바일은 2열 */
        }
    </style>
</head>
<body>
    <div class="container">
EOF

while read -r name url; do
    [[ -z "$name" || "$name" == "#"* ]] && continue
    echo "        <a href=\"$url\" class=\"link-item\">$name</a>" >> $OUTPUT
done < "$INPUT"

cat <<EOF >> $OUTPUT
    </div>
</body>
</html>
EOF

echo "성공: 새로운 스타일의 $OUTPUT 파일이 생성되었습니다."

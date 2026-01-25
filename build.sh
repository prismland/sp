#!/bin/bash

OUTPUT="index.html"
INPUT="list.txt"

# HTML 상단 및 스타일 작성
cat <<'EOF' > $OUTPUT
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Start page - gh</title>
    <style>
        body {
            background-color: #0f0f0f;
            color: #efefef;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px 0;
        }
        .header { text-align: center; margin-bottom: 30px; }
        #clock { font-size: 4rem; font-weight: 100; margin: 10px 0; letter-spacing: -2px; }
        #date { font-size: 1.2rem; color: #888; text-transform: uppercase; letter-spacing: 2px; }
        #weather { font-size: 1rem; color: #aaa; margin-top: 15px; font-weight: 300; line-height: 1.4; }

        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            width: 90%;
            max-width: 700px;
        }
        .link-item {
            flex: 1 1 140px;
            max-width: 220px;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 60px;
            background-color: #1a1a1a;
            color: #fff;
            text-decoration: none;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #333;
            transition: 0.2s;
            /* text-transform: uppercase; 삭제됨: 이제 대소문자 유지 */
        }
        .link-item:hover { background-color: #eee; color: #000; transform: translateY(-2px); }
        
        .spacer {
            flex-basis: 100%;
            height: 30px;
        }

        @media (max-width: 480px) {
            .link-item { flex: 1 1 40%; }
            #clock { font-size: 3rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div id="date"></div>
        <div id="clock">00:00:00</div>
        <div id="weather">Loading weather...</div>
    </div>
    <div class="container">
EOF

# list.txt 한 줄씩 읽기 (대소문자 및 빈줄 처리)
while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^# ]]; then
        continue
    elif [[ -z "$line" ]]; then
        echo "        <div class=\"spacer\"></div>" >> $OUTPUT
    else
        # 첫 번째 공백을 기준으로 이름과 URL 분리
        name=$(echo "$line" | awk '{print $1}')
        url=$(echo "$line" | awk '{print $2}')
        # 새 창 열기(_blank) 속성 추가
        echo "        <a href=\"$url\" class=\"link-item\" target=\"_blank\" rel=\"noopener noreferrer\">$name</a>" >> $OUTPUT
    fi
done < "$INPUT"

# 하단 자바스크립트 작성
cat <<'EOF' >> $OUTPUT
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = h + ":" + m + ":" + s;
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('date').textContent = now.toLocaleDateString('en-US', options);
        }
        async function updateWeather() {
            try {
                const response = await fetch('https://wttr.in/Jinju?m&format=%c+%C+%t+(Feels+%f)+%w');
                const data = await response.text();
                document.getElementById('weather').textContent = "Jinju: " + data;
            } catch (e) { document.getElementById('weather').textContent = "Weather unavailable"; }
        }
        setInterval(updateClock, 1000);
        updateClock();
        updateWeather();
        setInterval(updateWeather, 1800000);
    </script>
</body>
</html>
EOF

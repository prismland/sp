#!/bin/bash

OUTPUT="index.html"
INPUT="list.txt"

cat <<EOF > $OUTPUT
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
            flex: 1 1 140px; /* 기본 크기 140px, 공간 있으면 늘어남 */
            max-width: 220px;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 60px;
            background-color: #1a1a1a;
            color: #fff;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #333;
            transition: 0.2s;
            text-transform: uppercase;
        }
        .link-item:hover { background-color: #eee; color: #000; transform: translateY(-2px); }
        
        /* 빈 줄(섹션 구분)을 위한 스타일 */
        .spacer {
            flex-basis: 100%;
            height: 30px; /* 비어있는 줄의 높이 */
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

# list.txt 한 줄씩 읽기
while IFS= read -r line || [[ -n "$line" ]]; do
    # 1. 주석 처리 (#으로 시작하는 줄 무시)
    if [[ "$line" =~ ^# ]]; then
        continue
    # 2. 빈 줄 처리 (HTML에서 공간 비우기)
    elif [[ -z "$line" ]]; then
        echo "        <div class=\"spacer\"></div>" >> $OUTPUT
    # 3. 정상 링크 처리
    else
        read -r name url <<< "$line"
        echo "        <a href=\"$url\" class=\"link-item\">$name</a>" >> $OUTPUT
    fi
done < "$INPUT"

cat <<EOF >> $OUTPUT
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

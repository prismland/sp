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
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        #clock {
            font-size: 4rem;
            font-weight: 100;
            margin: 10px 0;
            letter-spacing: -2px;
        }

        #date {
            font-size: 1.2rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        #weather {
            font-size: 1.1rem;
            color: #aaa;
            margin-top: 15px;
            font-weight: 300;
        }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            width: 90%;
            max-width: 700px;
        }

        .link-item {
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

        .link-item:hover {
            background-color: #eee;
            color: #000;
            transform: translateY(-2px);
        }

        @media (max-width: 480px) {
            .container { grid-template-columns: repeat(2, 1fr); }
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

while read -r name url; do
    [[ -z "$name" || "$name" == "#"* ]] && continue
    echo "        <a href=\"$url\" class=\"link-item\">$name</a>" >> $OUTPUT
done < "$INPUT"

cat <<EOF >> $OUTPUT
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            
            // 시간 표시 (24시간 형식)
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = h + ":" + m + ":" + s;
            
            // 영어 Full Format 날짜 (예: Sunday, January 25, 2026)
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('date').textContent = now.toLocaleDateString('en-US', options);
        }

        // wttr.in을 이용한 텍스트 날씨 가져오기 (진주)
        async function updateWeather() {
            try {
                // 진주시 날씨를 한 줄 텍스트 형식으로 요청
                const response = await fetch('https://wttr.in/Jinju?format=%C+%t');
                const data = await response.text();
                document.getElementById('weather').textContent = "Jinju: " + data;
            } catch (error) {
                document.getElementById('weather').textContent = "Weather unavailable";
            }
        }

        setInterval(updateClock, 1000);
        updateClock();
        updateWeather();
        // 날씨는 30분마다 업데이트
        setInterval(updateWeather, 1800000);
    </script>
</body>
</html>
EOF

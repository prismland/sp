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
            background-color: #0f0f0f;
            color: #efefef;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }

        /* 상단 정보 영역 (시계 & 날씨) */
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        #clock {
            font-size: 3.5rem;
            font-weight: 200;
            margin: 0;
        }
        #date {
            font-size: 1.2rem;
            color: #888;
            margin-bottom: 20px;
        }
        .weather-container {
            margin-top: 10px;
            border-radius: 15px;
            overflow: hidden;
            opacity: 0.8;
        }

        /* 링크 그리드 영역 */
        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            width: 90%;
            max-width: 600px;
        }
        .link-item {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 70px;
            background-color: #1a1a1a;
            color: #ffffff;
            text-decoration: none;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 12px;
            border: 1px solid #333;
            transition: all 0.2s;
            text-transform: uppercase;
        }
        .link-item:hover {
            background-color: #333;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        }
        @media (max-width: 480px) {
            .container { grid-template-columns: repeat(2, 1fr); }
            #clock { font-size: 2.5rem; }
        }
    </style>
</head>
<body>

    <div class="header">
        <p id="date"></p>
        <h1 id="clock">00:00:00</h1>
        
        <div class="weather-container">
            <a class="weatherwidget-io" href="https://weatherwidget.io/w/412662/jinju/" data-label_1="JINJU" data-label_2="WEATHER" data-font="Roboto" data-icons="Climacons Animated" data-theme="pure" data-basecolor="#0f0f0f" data-accent="rgba(255, 255, 255, 0)" data-textcolor="#ffffff" >JINJU WEATHER</a>
            <script>
            !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
            </script>
        </div>
    </div>

    <div class="container">
EOF

# list.txt를 읽어 링크 생성
while read -r name url; do
    [[ -z "$name" || "$name" == "#"* ]] && continue
    echo "        <a href=\"$url\" class=\"link-item\">$name</a>" >> $OUTPUT
done < "$INPUT"

cat <<EOF >> $OUTPUT
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            
            // 시간 표시
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = \`\${h}:\${m}:\${s}\`;
            
            // 날짜 표시
            const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
            document.getElementById('date').textContent = now.toLocaleDateString('ko-KR', options);
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
</body>
</html>
EOF

echo "성공: 날짜, 시간, 진주 날씨가 포함된 $OUTPUT 파일이 생성되었습니다."

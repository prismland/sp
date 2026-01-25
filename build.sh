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

        .header {
            text-align: center;
            margin-bottom: 20px;
            width: 100%;
        }

        #clock {
            font-size: 3.5rem;
            font-weight: 200;
            margin: 10px 0;
        }

        #date {
            font-size: 1.1rem;
            color: #888;
        }

        /* 날씨 위젯 영역 - 최소 높이를 지정하여 공간 확보 */
        .weather-section {
            width: 100%;
            max-width: 400px;
            margin: 0 auto 30px auto;
            min-height: 100px; 
        }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 15px;
            width: 90%;
            max-width: 600px;
        }

        .link-item {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 65px;
            background-color: #1a1a1a;
            color: #ffffff;
            text-decoration: none;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 12px;
            border: 1px solid #333;
            transition: all 0.2s;
            text-transform: uppercase;
        }

        .link-item:hover {
            background-color: #333;
            transform: translateY(-3px);
            border-color: #555;
        }

        @media (max-width: 480px) {
            .container { grid-template-columns: repeat(2, 1fr); }
            #clock { font-size: 2.8rem; }
        }
    </style>
</head>
<body>

    <div class="header">
        <div id="date"></div>
        <div id="clock">00:00:00</div>
    </div>

    <div class="weather-section">
        <a class="weatherwidget-io" href="https://weatherwidget.io/w/412662/jinju/" 
           data-label_1="JINJU" 
           data-label_2="WEATHER" 
           data-font="Roboto" 
           data-icons="Climacons Animated" 
           data-theme="pure" 
           data-basecolor="#0f0f0f" 
           data-textcolor="#ffffff" >JINJU WEATHER</a>
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
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = h + ":" + m + ":" + s;
            
            const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' };
            document.getElementById('date').textContent = now.toLocaleDateString('ko-KR', options);
        }
        setInterval(updateClock, 1000);
        updateClock();

        /* 위젯 스크립트 강제 로드 */
        !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
    </script>
</body>
</html>
EOF

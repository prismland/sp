#!/bin/bash

OUTPUT="index.html"
INPUT="list.txt"

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
        #date { 
            font-size: 1.2rem; 
            color: #888; 
            letter-spacing: 1px;
            /* text-transform: uppercase 제거하여 JS에서 설정한 포맷 유지 */
        }
        #weather { font-size: 1rem; color: #aaa; margin-top: 15px; font-weight: 300; line-height: 1.4; }

        /* 메인 및 섹션 공통 컨테이너 */
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-content: center;
            gap: 15px;
            width: 100%;
            max-width: 700px;
            margin: 0 auto;
        }
        
        /* 접이식 섹션 스타일 보정 */
        details {
            width: 100%;
            max-width: 700px;
            margin-top: 20px;
        }
        summary {
            cursor: pointer;
            color: #555;
            font-size: 0.9rem;
            list-style: none;
            transition: 0.3s;
            padding: 15px;
            text-align: center;
            user-select: none;
        }
        summary:hover { color: #fff; }
        summary::before { content: "+ "; }
        details[open] summary::before { content: "- "; }

        /* 펼쳐졌을 때 내부 컨테이너 정렬 */
        details .container {
            display: flex;
            justify-content: center;
            padding: 10px 0;
        }

        .link-item {
            flex: 0 1 140px; /* 고정 너비 기반으로 정렬 유지 */
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
        }
        .link-item:hover { background-color: #eee; color: #000; transform: translateY(-2px); }
        
        .spacer { flex-basis: 100%; height: 30px; }

        @media (max-width: 480px) {
            .link-item { flex: 0 1 44%; }
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

IN_DETAILS=false

while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^# ]]; then
        continue
    elif [[ "$line" =~ ^\> ]]; then
        if [ "$IN_DETAILS" = true ]; then
            echo "        </div></details>" >> $OUTPUT
        fi
        TITLE=$(echo "$line" | sed 's/^>//' | xargs)
        echo "        <details><summary>$TITLE</summary><div class=\"container\">" >> $OUTPUT
        IN_DETAILS=true
    elif [[ -z "$line" ]]; then
        echo "        <div class=\"spacer\"></div>" >> $OUTPUT
    else
        name=$(echo "$line" | awk '{print $1}')
        url=$(echo "$line" | awk '{print $2}')
        echo "        <a href=\"$url\" class=\"link-item\" target=\"_blank\" rel=\"noopener noreferrer\">$name</a>" >> $OUTPUT
    fi
done < "$INPUT"

if [ "$IN_DETAILS" = true ]; then
    echo "        </div></details>" >> $OUTPUT
fi

cat <<'EOF' >> $OUTPUT
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = h + ":" + m + ":" + s;
            
            // 앞글자만 대문자인 영어 날짜 형식 (예: Sunday, January 25, 2026)
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

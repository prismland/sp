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
        
        /* 접이식 섹션 스타일 */
        details {
            width: 100%;
            margin-top: 20px;
            text-align: center;
        }
        summary {
            cursor: pointer;
            color: #666;
            font-size: 0.9rem;
            list-style: none; /* 기본 화살표 숨기기 */
            transition: 0.3s;
            padding: 10px;
        }
        summary:hover { color: #fff; }
        summary::before { content: "+ "; }
        details[open] summary::before { content: "- "; }

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
            margin: 7.5px; /* 컨테이너 안에서 간격 유지 */
        }
        .link-item:hover { background-color: #eee; color: #000; transform: translateY(-2px); }
        
        .spacer { flex-basis: 100%; height: 30px; }

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

IN_DETAILS=false

while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^# ]]; then
        continue
    elif [[ "$line" =~ ^\> ]]; then
        # '>'로 시작하면 접이식 섹션 시작
        if [ "$IN_DETAILS" = true ]; then
            echo "        </div></details>" >> $OUTPUT
        fi
        TITLE=$(echo "$line" | sed 's/^>//' | xargs)
        echo "        <details><summary>$TITLE</summary><div class=\"container\" style=\"margin-top:10px;\">" >> $OUTPUT
        IN_DETAILS=true
    elif [[ -z "$line" ]]; then
        echo "        <div class=\"spacer\"></div>" >> $OUTPUT
    else
        name=$(echo "$line" | awk '{print $1}')
        url=$(echo "$line" | awk '{print $2}')
        echo "        <a href=\"$url\" class=\"link-item\" target=\"_blank\" rel=\"noopener noreferrer\">$name</a>" >> $OUTPUT
    fi
done < "$INPUT"

# 열려있는 details 태그 닫기
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

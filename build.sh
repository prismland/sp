#!/bin/bash
# Functions: updateClock(), updateWeather()

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
        #date { font-size: 1.2rem; color: #888; letter-spacing: 1px; }
        #weather { font-size: 1rem; color: #aaa; margin-top: 15px; font-weight: 300; line-height: 1.4; }

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
        
        details { width: 100%; max-width: 700px; margin-top: 20px; }
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
        details .container { display: flex; justify-content: center; padding: 10px 0; }

        .link-item {
            flex: 0 1 140px;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 60px;
            background-color: #1a1a1a;
            color: #fff;
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #333;
            transition: 0.2s;
            text-align: center;
            padding: 0 5px;
        }
        .link-item:hover { background-color: #eee; color: #000; transform: translateY(-2px); }

        /* 특수 상태 스타일 */
        .login-required { border-color: #2b5a82; } /* 로그인: 푸른색 테두리 */
        .update-needed { border-color: #825a2b; }  /* 주소변경: 주황색 테두리 */
        
        .spacer { flex-basis: 100%; height: 30px; }

        @media (max-width: 480px) {
            .link-item { flex: 0 1 44%; font-size: 0.85rem; }
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
        
        display_name=$name
        item_class="link-item"

        # [L] 로그인 필요 -> 🔑
        if [[ "$name" == *"[L]"* ]]; then
            display_name="🔑 ${name//\[L\]/}"
            item_class="$item_class login-required"
        fi
        # [T] 번역 필요 -> 🌐
        if [[ "$name" == *"[T]"* ]]; then
            display_name="🌐 ${name//\[T\]/}"
        fi
        # [U] 주소 변경 잦음 -> ⚠️
        if [[ "$name" == *"[U]"* ]]; then
            display_name="⚠️ ${name//\[U\]/}"
            item_class="$item_class update-needed"
        fi

        echo "        <a href=\"$url\" class=\"$item_class\" target=\"_blank\" rel=\"noopener noreferrer\">$display_name</a>" >> $OUTPUT
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
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('date').textContent = now.toLocaleDateString('en-US', options);
        }

        async function updateWeather() {
            try {
                const response = await fetch('https://wttr.in/Jinju?format=%c+%C+%t+(Feels+%f)+%w');
                let data = await response.text();
                // km/h -> m/s 자체 변환 로직
                data = data.replace(/([0-9.]+)\s*km\/h/g, function(match, p1) {
                    return (parseFloat(p1) / 3.6).toFixed(1) + "m/s";
                });
                document.getElementById('weather').textContent = "Jinju: " + data;
            } catch (e) { 
                document.getElementById('weather').textContent = "Weather unavailable"; 
            }
        }

        setInterval(updateClock, 1000);
        updateClock();
        updateWeather();
        setInterval(updateWeather, 1800000);
    </script>
</body>
</html>
EOF

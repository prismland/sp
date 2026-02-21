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
            justify-content: flex-start;
            min-height: 100vh;
            padding: 20px 0; /* 상하 여백 축소 */
        }
        .header { text-align: center; margin-bottom: 20px; }
        #clock { font-size: 4rem; font-weight: 100; margin: 5px 0; letter-spacing: -2px; }
        #date { font-size: 1.1rem; color: #888; letter-spacing: 1px; }
        #weather { font-size: 0.9rem; color: #aaa; margin-top: 10px; font-weight: 300; }

        .container {
            display: grid;
            /* 5개 제한 없이 화면 꽉 차게 설정 */
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 10px;
            width: 98%;
            max-width: 1200px; /* 더 넓은 화면 대응 */
            margin: 0 auto;
        }
        
        details { width: 98%; max-width: 1200px; margin-bottom: 5px; } /* 카테고리 간격 축소 */
        summary {
            cursor: pointer;
            color: #444;
            font-size: 0.85rem;
            list-style: none;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            transition: 0.3s;
        }
        summary:hover { color: #fff; }
        summary::before { content: "[ "; }
        summary::after { content: " ]"; }

        .link-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 50px;
            padding: 0 12px;
            background-color: #161616;
            color: #fff;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            border-radius: 6px;
            border: 1px solid #2a2a2a;
            transition: 0.2s;
        }
        .link-item:hover { background-color: #eee; color: #000; transform: translateY(-1px); }
        .item-name { flex-grow: 1; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .icon-box { width: 20px; display: flex; justify-content: center; }

        .login-required { border-color: #1e3a5f; }
        .update-needed { border-color: #5f3a1e; }
        
        .spacer { grid-column: 1 / -1; height: 10px; }

        @media (max-width: 480px) {
            #clock { font-size: 2.5rem; }
            .container { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
        }
    </style>
</head>
<body>
    <div class="header">
        <div id="date"></div>
        <div id="clock">00:00:00</div>
        <div id="weather">Loading weather...</div>
    </div>
EOF

TOTAL_SECTIONS=$(grep -c "^>" "$INPUT")
CURRENT_SECTION=0

while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ ^# ]] && continue
    
    if [[ "$line" =~ ^\> ]]; then
        ((CURRENT_SECTION++))
        [ $CURRENT_SECTION -gt 1 ] && echo "    </div></details>" >> $OUTPUT
        TITLE=$(echo "$line" | sed 's/^>//' | xargs)
        # 마지막 섹션만 접힌 상태로 시작 [cite: 2]
        STATE=$([ "$CURRENT_SECTION" -lt "$TOTAL_SECTIONS" ] && echo "open" || echo "")
        echo "    <details $STATE><summary>$TITLE</summary><div class=\"container\">" >> $OUTPUT
    elif [[ -z "$line" ]]; then
        echo "        <div class=\"spacer\"></div>" >> $OUTPUT
    else
        name=$(echo "$line" | awk '{print $1}')
        url=$(echo "$line" | awk '{print $2}')
        
        # 숫자나 일반 문자가 아닌 '순수 이모지'만 분리하는 로직 [cite: 2]
        icon_left=$(echo "$name" | grep -oP "^[\x{1F300}-\x{1F9FF}\x{2600}-\x{26FF}]" 2>/dev/null)
        clean_name=${name#$icon_left}
        
        icon_right=""
        item_class="link-item"

        [[ "$name" == *"[L]"* ]] && icon_right="🔑" && clean_name=${clean_name//\[L\]/} && item_class="$item_class login-required"
        [[ "$name" == *"[T]"* ]] && icon_right="${icon_right}🌐" && clean_name=${clean_name//\[T\]/}
        [[ "$name" == *"[U]"* ]] && icon_right="${icon_right}⚠️" && clean_name=${clean_name//\[U\]/} && item_class="$item_class update-needed"

        echo "        <a href=\"$url\" class=\"$item_class\" target=\"_blank\" rel=\"noopener noreferrer\">" >> $OUTPUT
        echo "            <span class=\"icon-box\">$icon_left</span>" >> $OUTPUT
        echo "            <span class=\"item-name\">$clean_name</span>" >> $OUTPUT
        echo "            <span class=\"icon-box\">$icon_right</span>" >> $OUTPUT
        echo "        </a>" >> $OUTPUT
    fi
done < "$INPUT"

echo "    </div></details>" >> $OUTPUT

cat <<'EOF' >> $OUTPUT
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').textContent = now.toTimeString().split(' ')[0];
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('date').textContent = now.toLocaleDateString('en-US', options);
        }
        async function updateWeather() {
            try {
                const response = await fetch('https://wttr.in/Jinju?format=%c+%C+%t+(Feels+%f)+%w');
                let data = await response.text();
                // km/h -> m/s 변환 [cite: 2]
                data = data.replace(/([0-9.]+)\s*km\/h/g, (m, p1) => (p1/3.6).toFixed(1) + "m/s");
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

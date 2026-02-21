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
            background-color: #0d0d0d;
            color: #efefef;
            font-family: 'Segoe UI', Roboto, -apple-system, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            min-height: 100vh;
            padding: 20px 0;
        }
        .header { text-align: center; margin-bottom: 25px; }
        #clock { font-size: 4.5rem; font-weight: 200; margin: 5px 0; letter-spacing: -2px; color: #fff; }
        #date { font-size: 1.1rem; color: #999; letter-spacing: 1px; }
        #weather { font-size: 0.95rem; color: #bbb; margin-top: 10px; }

        .container {
            display: grid;
            /* 버튼 최소 가로 너비를 130px -> 170px로 상향 조정 */
            grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
            gap: 12px;
            width: 98%;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        details { width: 98%; max-width: 1600px; margin-bottom: 5px; }
        summary {
            cursor: pointer;
            color: #444;
            font-size: 0.85rem;
            list-style: none;
            padding: 10px;
            text-align: center;
            transition: 0.3s;
        }
        summary:hover { color: #888; }
        summary::before { content: "[ "; }
        summary::after { content: " ]"; }

        .link-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 52px;
            padding: 0 12px;
            background-color: #161616;
            color: #efefef;
            text-decoration: none;
            font-size: 0.88rem; /* 글자 크기를 살짝 줄여 더 많이 들어가게 조정 */
            font-weight: 400;
            border-radius: 6px;
            border: 1px solid #2a2a2a;
            transition: all 0.2s;
            overflow: hidden;
        }
        .link-item:hover { 
            background-color: #eee; 
            color: #000; 
            transform: translateY(-1px);
        }
        
        /* 텍스트 정렬 및 잘림 방지 보강 */
        .item-name { 
            flex-grow: 1; 
            text-align: center; 
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis; 
            padding: 0 8px;
            letter-spacing: -0.2px; /* 자간을 미세하게 좁힘 */
        }
        
        .icon-box { 
            min-width: 28px; 
            display: flex; 
            justify-content: center; 
            font-size: 1.25rem; 
        }

        .login-required { border-color: #1e3a5f; }
        .update-needed { border-color: #5f3a1e; }
        
        .spacer { grid-column: 1 / -1; height: 10px; }

        @media (max-width: 480px) {
            #clock { font-size: 3rem; }
            /* 모바일에서도 버튼이 너무 작아지지 않게 조정 */
            .container { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
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
        STATE=$([ "$CURRENT_SECTION" -lt "$TOTAL_SECTIONS" ] && echo "open" || echo "")
        echo "    <details $STATE><summary>$TITLE</summary><div class=\"container\">" >> $OUTPUT
    elif [[ -z "$line" ]]; then
        echo "        <div class=\"spacer\"></div>" >> $OUTPUT
    else
        name=$(echo "$line" | awk '{print $1}')
        url=$(echo "$line" | awk '{print $2}')
        
        icon_left=$(echo "$name" | grep -oP "^(\p{Emoji_Presentation}|\p{Emoji}\x{FE0F})(\x{200D}\p{Emoji})*" 2>/dev/null)
        clean_name=${name#$icon_left}
        
        icon_right=""
        item_class="link-item"

        if [[ "$clean_name" == *"[L]"* ]]; then
            icon_right="🔑"
            clean_name=${clean_name//\[L\]/}
            item_class="$item_class login-required"
        fi
        if [[ "$clean_name" == *"[T]"* ]]; then
            icon_right="${icon_right}🌐"
            clean_name=${clean_name//\[T\]/}
        fi
        if [[ "$clean_name" == *"[U]"* ]]; then
            icon_right="${icon_right}⚠️"
            clean_name=${clean_name//\[U\]/}
            item_class="$item_class update-needed"
        fi

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

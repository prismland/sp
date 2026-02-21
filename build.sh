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
            background-color: #0d0d0d; /* 조금 더 깊은 블랙으로 배경 변경 */
            color: #ffffff; /* 텍스트를 순백색으로 변경하여 대비 강화 */
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
        #date { font-size: 1.1rem; color: #999; letter-spacing: 1px; font-weight: 400; }
        #weather { font-size: 0.95rem; color: #bbb; margin-top: 10px; font-weight: 400; }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 12px;
            width: 98%;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        details { width: 98%; max-width: 1400px; margin-bottom: 8px; }
        summary {
            cursor: pointer;
            color: #555; /* 카테고리 제목 시인성 조절 */
            font-size: 0.85rem;
            list-style: none;
            padding: 10px;
            text-align: center;
            font-weight: 700;
            text-transform: uppercase;
            transition: 0.3s;
        }
        summary:hover { color: #aaa; }
        summary::before { content: "[ "; }
        summary::after { content: " ]"; }

        .link-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 52px;
            padding: 0 12px;
            background-color: #1a1a1a; /* 버튼 배경을 약간 밝게 하여 입체감 부여 */
            color: #efefef;
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #333; /* 테두리를 조금 더 명확하게 */
            transition: all 0.2s ease-in-out;
        }
        .link-item:hover { 
            background-color: #ffffff; 
            color: #000000; 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255,255,255,0.1); /* 호버 시 미세한 광원 효과 */
        }
        .item-name { flex-grow: 1; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 6px; }
        
        /* 이모지 박스 크기 키움 */
        .icon-box { 
            min-width: 28px; 
            display: flex; 
            justify-content: center; 
            font-size: 1.35rem; /* 이모지 크기를 조금 더 키움 */
            filter: drop-shadow(0 0 2px rgba(0,0,0,0.5)); /* 이모지 선명도 보강 */
        }

        /* 상태 태그 테두리 강조 */
        .login-required { border-color: #316ba1; border-width: 1.2px; }
        .update-needed { border-color: #a16b31; border-width: 1.2px; }
        
        .spacer { grid-column: 1 / -1; height: 12px; }

        @media (max-width: 480px) {
            #clock { font-size: 3rem; }
            .container { grid-template-columns: repeat(auto-fill, minmax(135px, 1fr)); }
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
        
        # 복합 이모지 및 그래픽 변환 기호 완벽 감지
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

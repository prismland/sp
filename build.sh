#!/bin/bash
# Version: 2026-03-08-v03 | Description: Add weather icons from OpenWeatherMap
# Functions: updateClock(), updateWeather()

OUTPUT="index.html"
INPUT="list.txt"

# [설정] OpenWeatherMap API 키와 도시 ID
API_KEY="e3a8c001ebfb94e9b545af6d4dcc3d15"
CITY_ID="1846052"

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
        
        /* 날씨 영역 스타일: 아이콘과 텍스트를 가로로 정렬 */
        #weather { 
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem; 
            color: #bbb; 
            margin-top: 5px; 
        }
        #weather img {
            width: 40px; /* 아이콘 크기 조절 */
            height: 40px;
            margin-right: -5px; /* 텍스트와의 간격 조절 */
            filter: drop-shadow(0 0 5px rgba(255,255,255,0.2)); /* 아이콘 가독성 보강 */
        }

        .container {
            display: grid;
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
            font-size: 0.88rem;
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
        
        .item-name { 
            flex-grow: 1; 
            text-align: center; 
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis; 
            padding: 0 8px;
            letter-spacing: -0.2px;
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

# [기존 list.txt 처리 루프 동일]
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
        if [[ "$clean_name" == *"[L]"* ]]; then icon_right="🔑"; clean_name=${clean_name//\[L\]/}; item_class="$item_class login-required"; fi
        if [[ "$clean_name" == *"[T]"* ]]; then icon_right="${icon_right}🌐"; clean_name=${clean_name//\[T\]/}; fi
        if [[ "$clean_name" == *"[U]"* ]]; then icon_right="${icon_right}⚠️"; clean_name=${clean_name//\[U\]/}; item_class="$item_class update-needed"; fi
        echo "        <a href=\"$url\" class=\"$item_class\" target=\"_blank\" rel=\"noopener noreferrer\">" >> $OUTPUT
        echo "            <span class=\"icon-box\">$icon_left</span>" >> $OUTPUT
        echo "            <span class=\"item-name\">$clean_name</span>" >> $OUTPUT
        echo "            <span class=\"icon-box\">$icon_right</span>" >> $OUTPUT
        echo "        </a>" >> $OUTPUT
    fi
done < "$INPUT"
echo "    </div></details>" >> $OUTPUT

# 자바스크립트 섹션: 아이콘 이미지 로직 추가
cat <<EOF >> $OUTPUT
    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').textContent = now.toTimeString().split(' ')[0];
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('date').textContent = now.toLocaleDateString('en-US', options);
        }

        async function updateWeather() {
            const apiKey = "$API_KEY";
            const cityId = "$CITY_ID";
            const url = \`https://api.openweathermap.org/data/2.5/weather?id=\${cityId}&units=metric&appid=\${apiKey}\`;

            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error('Weather API Error');
                const json = await response.json();
                
                const iconCode = json.weather[0].icon;
                const desc = json.weather[0].description;
                const temp = json.main.temp.toFixed(0);
                const feels = json.main.feels_like.toFixed(0);
                const wind = json.wind.speed.toFixed(1);
                
                // 아이콘 이미지 태그 생성 (OpenWeatherMap 제공 경로)
                const iconHtml = \`<img src="https://openweathermap.org/img/wn/\${iconCode}@2x.png" alt="\${desc}">\`;
                
                // HTML로 삽입하여 아이콘과 텍스트를 함께 표시
                document.getElementById('weather').innerHTML = 
                    \`\${iconHtml} Jinju: \${desc} \${temp}°C (Feels \${feels}°C) \${wind}m/s\`;
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

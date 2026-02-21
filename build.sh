#!/bin/bash
# Functions: updateClock(), updateWeather()

OUTPUT="index.html"
INPUT="list.txt"

# HTML 헤더 및 스타일
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
            padding: 40px 0;
        }
        .header { text-align: center; margin-bottom: 30px; }
        #clock { font-size: 4rem; font-weight: 100; margin: 10px 0; letter-spacing: -2px; }
        #date { font-size: 1.2rem; color: #888; letter-spacing: 1px; }
        #weather { font-size: 0.95rem; color: #aaa; margin-top: 15px; font-weight: 300; }

        .container {
            display: grid;
            /* 화면 넓이에 따라 버튼 수 유동적 조절 (최소 140px) */
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            width: 95%;
            max-width: 900px;
            margin: 0 auto;
        }
        
        details { width: 95%; max-width: 900px; margin-bottom: 20px; }
        summary {
            cursor: pointer;
            color: #666;
            font-size: 1rem;
            list-style: none;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            letter-spacing: 2px;
            transition: 0.3s;
        }
        summary:hover { color: #fff; }
        summary::before { content: ":: "; }
        summary::after { content: " ::"; }

        .link-item {
            display: flex;
            justify-content: space-between; /* 이모지 양끝 배치 */
            align-items: center;
            height: 55px;
            padding: 0 15px;
            background-color: #1a1a1a;
            color: #fff;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            border-radius: 8px;
            border: 1px solid #333;
            transition: 0.2s;
        }
        .link-item:hover { background-color: #eee; color: #000; transform: translateY(-2px); }
        .item-name { flex-grow: 1; text-align: center; }

        .login-required { border-color: #2b5a82; }
        .update-needed { border-color: #825a2b; }
        
        .spacer { grid-column: 1 / -1; height: 20px; }

        @media (max-width: 480px) {
            #clock { font-size: 3rem; }
            .container { grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
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

# 섹션 개수 파악 (마지막 섹션만 접기 위함)
TOTAL_SECTIONS=$(grep -c "^>" "$INPUT")
CURRENT_SECTION=0

while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^# ]]; then
        continue
    elif [[ "$line" =~ ^\> ]]; then
        ((CURRENT_SECTION++))
        if [ $CURRENT_SECTION -gt 1 ]; then echo "    </div></details>" >> $OUTPUT; fi
        
        TITLE=$(echo "$line" | sed 's/^>//' | xargs)
        # 마지막 섹션이 아니면 'open' 속성 부여 (펼쳐진 상태)
        if [ "$CURRENT_SECTION" -lt "$TOTAL_SECTIONS" ]; then
            echo "    <details open><summary>$TITLE</summary><div class=\"container\">" >> $OUTPUT
        else
            echo "    <details><summary>$TITLE</summary><div class=\"container\">" >> $OUTPUT
        fi
    elif [[ -z "$line" ]]; then
        echo "        <div class=\"spacer\"></div>" >> $OUTPUT
    else
        name=$(echo "$line" | awk '{print $1}')
        url=$(echo "$line" | awk '{print $2}')
        
        # 기본 이모지 추출 (이름 맨 앞 글자가 이모지인지 확인)
        icon_left=$(echo "$name" | grep -oP "^\p{Emoji}")
        clean_name=${name#$icon_left}
        
        icon_right=""
        item_class="link-item"

        if [[ "$name" == *"[L]"* ]]; then
            icon_right="🔑"
            clean_name=${clean_name//\[L\]/}
            item_class="$item_class login-required"
        fi
        if [[ "$name" == *"[T]"* ]]; then
            icon_right="${icon_right}🌐"
            clean_name=${clean_name//\[T\]/}
        fi
        if [[ "$name" == *"[U]"* ]]; then
            icon_right="${icon_right}⚠️"
            clean_name=${clean_name//\[U\]/}
            item_class="$item_class update-needed"
        fi

        echo "        <a href=\"$url\" class=\"$item_class\" target=\"_blank\" rel=\"noopener noreferrer\">" >> $OUTPUT
        echo "            <span>$icon_left</span>" >> $OUTPUT
        echo "            <span class=\"item-name\">$clean_name</span>" >> $OUTPUT
        echo "            <span>$icon_right</span>" >> $OUTPUT
        echo "        </a>" >> $OUTPUT
    fi
done < "$INPUT"

echo "    </div></details>" >> $OUTPUT

# 하단 스크립트
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

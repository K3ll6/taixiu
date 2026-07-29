from flask import Flask, request, jsonify
from google import genai
import os
import json
import traceback

app = Flask(__name__)

# Lay API Key tu bien moi truong GEMINI_API_KEY
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_KEY)

@app.route('/api/analyze', methods=['POST'])
def analyze_taixiu():
    try:
        data = request.get_json()
        if not data or 'sessions' not in data:
            return jsonify({"error": "Thieu du lieu lich su phien!"}), 400
        
        sessions = data['sessions']
        total_sessions = len(sessions)
        
        prompt = f"""
        Ban la mot chuyen gia phan tich xac suat va quy luat cau Tai Xiu trong game.
        Dưới đây la lich su {total_sessions} phien gan nhat theo thu tu tu cu den moi:
        {sessions}

        Nhiem vu cua ban:
        1. Phan tich cac dang cau.
        2. Quyet dinh cuoi cung: nen danh "TAI", "XIU", hay "SKIP".
        3. Viet giai thich ngan gon ly do (toi da 15 tu).
        4. De xuat so tien cuoc (mac dinh 1000 den 5000).

        YEU CAU: Tra ve ket qua hoan toan bang dinh dang JSON thuan tuy (khong kem markdown) voi cau truc:
        {{
            "prediction": "TAI",
            "info": "Mo ta ngan gon",
            "stake": 1000
        }}
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        ai_text = response.text.strip()
        if "```json" in ai_text:
            ai_text = ai_text.split("```json")[1].split("```")[0].strip()
        elif "```" in ai_text:
            ai_text = ai_text.split("```")[1].split("```")[0].strip()

        result_json = json.loads(ai_text)
        return jsonify(result_json), 200

    except Exception as e:
        traceback.print_exc()
        error_str = str(e)
        return jsonify({
            "prediction": "SKIP",
            "info": f"Loi Gemini: {error_str[:30]}",
            "stake": 1000
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

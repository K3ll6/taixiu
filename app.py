from flask import Flask, request, jsonify
from openai import OpenAI
import os
import json
import traceback

app = Flask(__name__)

# Lấy API Key từ biến môi trường
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "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")
client = OpenAI(api_key=OPENAI_KEY)

@app.route('/api/analyze', methods=['POST'])
def analyze_taixiu():
    try:
        data = request.get_json()
        if not data or 'sessions' not in data:
            return jsonify({"error": "Thiếu dữ liệu lịch sử phiên!"}), 400
        
        sessions = data['sessions']
        total_sessions = len(sessions)
        
        prompt = f"""
        Bạn là một chuyên gia phân tích xác suất và quy luật cầu Tài Xỉu trong game.
        Dưới đây là lịch sử {total_sessions} phiên gần nhất theo thứ tự từ cũ đến mới:
        {sessions}

        Nhiệm vụ của bạn:
        1. Phân tích các dạng cầu.
        2. Quyết định cuối cùng: nên đánh "TAI", "XIU", hay "SKIP".
        3. Viết giải thích ngắn gọn lý do (tối đa 15 từ).
        4. Đề xuất số tiền cược (mặc định 1000 đến 5000).

        YÊU CẦU: Trả về kết quả hoàn toàn bằng định dạng JSON thuần túy, không có text ngoài với cấu trúc sau:
        {{
            "prediction": "TAI",
            "info": "Mo ta ngan gon",
            "stake": 1000
        }}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Dùng gpt-3.5-turbo cho độ ổn định cao
            messages=[
                {"role": "system", "content": "You are a professional game strategy analyst. You must output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        ai_text = response.choices[0].message.content.strip()
        result_json = json.loads(ai_text)
        return jsonify(result_json), 200

    except Exception as e:
        # In log chi tiết trên console của Render
        traceback.print_exc()
        error_str = str(e)
        
        # Trả lỗi chi tiết về game để bạn biết chính xác bị gì
        return jsonify({
            "prediction": "SKIP",
            "info": f"Loi OpenAI: {error_str[:35]}",
            "stake": 1000
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

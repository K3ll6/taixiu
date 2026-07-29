from flask import Flask, request, jsonify
from openai import OpenAI
import os
import json

app = Flask(__name__)

# Khởi tạo OpenAI Client (Lấy API Key từ biến môi trường)
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
        1. Phân tích các dạng cầu (Cầu 1-1, Cầu 2-2, Cầu bệt, Cầu đảo, v.v.).
        2. Quyết định cuối cùng: nên đánh "TAI", "XIU", hay "SKIP".
        3. Viết giải thích ngắn gọn lý do (tối đa 15 từ).
        4. Đề xuất số tiền cược (mặc định 1000 đến 5000).

        YÊU CẦU BẮT BUỘC: Trả về kết quả dưới dạng JSON với các khóa chính xác:
        {{
            "prediction": "TAI hoặc XIU hoặc SKIP",
            "info": "Mô tả ngắn gọn cầu",
            "stake": 1000
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Hoặc gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a professional game strategy analyst. You must always respond with valid JSON matching the requested keys."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        ai_text = response.choices[0].message.content.strip()
        result_json = json.loads(ai_text)
        return jsonify(result_json), 200

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return jsonify({
            "prediction": "SKIP",
            "info": "Lỗi phân tích từ Server OpenAI",
            "stake": 1000
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

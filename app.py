from flask import Flask, request, jsonify
from google import genai
import os

app = Flask(__name__)

# Khởi tạo Gemini Client (Lấy API Key từ biến môi trường hoặc thay trực tiếp chuỗi key của bạn)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Iii3oPTsZHigl0mOiigybM2YGcbMAiT0n2GwzeAZ36fAY")
client = genai.Client(api_key=GEMINI_KEY)

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

        YÊU CẦU BẮT BUỘC: Trả về kết quả DUY NHẤT dạng JSON thuần túy:
        {{
            "prediction": "TAI hoặc XIU hoặc SKIP",
            "info": "Mô tả ngắn gọn cầu",
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

        import json
        result_json = json.loads(ai_text)
        return jsonify(result_json), 200

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return jsonify({
            "prediction": "SKIP",
            "info": "Lỗi phân tích từ Server AI",
            "stake": 1000
        }, 500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

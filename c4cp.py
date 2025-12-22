import threading
import time
import webbrowser
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ========== 설정 ==========
API_KEY = os.getenv("GROQ_API_KEY")  
SELECTED_MODEL = "llama-3.3-70b-versatile"
PORT = 5001

# Groq 클라이언트 초기화
client = Groq(api_key=API_KEY)

app = Flask(__name__)
CORS(app)

# ========== 라우트 ==========

@app.route('/', methods=['GET'])
def home():
    """홈페이지 - 기존 HTML 파일 제공"""
    html_files = ['c4cH.html', 'c4c.html', 'c4cM.html', 'index.html']
    
    for html_file in html_files:
        if os.path.exists(html_file):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"파일 읽기 오류 ({html_file}): {e}")
                continue
    
    return "<h1>HTML 파일을 찾을 수 없습니다.</h1>", 404

@app.route('/chat', methods=['POST'])
def chat():
    """HTML에서 /chat으로 보내는 요청 처리"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip() if data else ''
        
        if not message:
            return jsonify({'success': False, 'response': '질문을 입력해주세요.'})
        
        response = client.chat.completions.create(
            model=SELECTED_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 친절하고 유용한 AI 어시스턴트입니다. 한국어로 자연스럽게 답변해주세요."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.7,
            max_tokens=2048,
            stream=False
        )
        
        answer = response.choices[0].message.content
        return jsonify({'success': True, 'response': answer})
        
    except Exception as e:
        return jsonify({'success': False, 'response': f'오류: {str(e)}'})

@app.route('/ask', methods=['POST'])
def ask():
    """HTML에서 /ask로 보내는 요청 처리"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip() if data else ''
        
        if not query:
            return jsonify({'success': False, 'message': '질문을 입력해주세요.'})
        
        response = client.chat.completions.create(
            model=SELECTED_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 친절하고 유용한 AI 어시스턴트입니다. 한국어로 자연스럽게 답변해주세요."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.7,
            max_tokens=2048,
            stream=False
        )
        
        answer = response.choices[0].message.content
        return jsonify({'success': True, 'result': {'answer': answer}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

# ========== 웹 서버 ==========

def run_web_server():
    """Flask 웹 서버 실행"""
    app.run(debug=False, host='0.0.0.0', port=PORT, use_reloader=False)

# ========== 메인 실행 ==========

if __name__ == "__main__":
    print("🚀 Groq 챗봇 시작!")
    
    # API 키 확인
    if not API_KEY:
        print("⚠️ API_KEY가 설정되지 않았습니다!")
        print("프로젝트 폴더에 .env 파일을 만들고 다음과 같이 작성하세요:")
        print("GROQ_API_KEY=your_api_key_here")
        exit()
    
    # 웹 서버를 별도 스레드에서 실행
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    time.sleep(2)
    print(f"✅ 웹 서버 실행됨: http://localhost:{PORT}")
    
    # 브라우저 자동 열기
    try:
        webbrowser.open(f'http://localhost:{PORT}')
        print("🌐 브라우저가 자동으로 열렸습니다.")
    except:
        print("⚠️ 브라우저를 수동으로 열어주세요.")
    
    # 서버를 계속 실행 (터미널 챗봇 없이)
    print("\n" + "="*50)
    print("💡 웹 브라우저에서 챗봇을 사용하세요!")
    print("🛑 종료하려면 Ctrl+C를 누르세요")
    print("="*50 + "\n")
    
    try:
        # 메인 스레드를 계속 살려둠
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 챗봇을 종료합니다!")
        print("서버가 중지되었습니다.")
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import pickle, hmac, hashlib, os, re

app = Flask(__name__)

SECRET_KEY = "pickle_tickle"
# openai.api_key = os.getenv("OPENAI_API_KEY") # 환경변수/코드에 key 삽입

FORBIDDEN_KEYWORDS = [r"\bflag\b", r"\bsecret\b", r"\bhmac\b", r"\bkey\b"]

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/load")
def load():
    username = request.args.get("user")
    sig = request.args.get("sig")
    if not username or not sig:
        return "Missing parameters", 400
    
    filepath = os.path.join("/", username + ".pkl")
    if not os.path.isfile(filepath):
        return "File not found", 404
    
    with open(filepath, "rb") as f:
        data = f.read()

    if not verify_sig(data, sig):
        return "Invalid signature", 403

    try:
        obj = pickle.loads(data)
    except Exception as e:
        return f"Deserialization error: {e}", 500

    return f"Loaded data: {str(obj)}"

def verify_sig(data, sig):
    computed = hmac.new(SECRET_KEY.encode(), data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, sig)


# 파일 업로드 구현
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    sig = request.form.get("sig") # HMAC verify

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = file.filename
    ext = os.path.splitext(filename)[-1].lower()

    # extension filter
    if ext not in [".jpg", ".png", ".pkl"]:
        return jsonify({"error" : "Invalid file type."}), 400
    
    # HMAC verification is possible only if the file contents are read first.
    data = file.read()

    # HMAC verification
    if ext == ".pkl" and not sig:
        return jsonify({"error":"Missing something..."}), 400
    
    if ext == ".pkl" and not verify_sig(data, sig):
        return jsonify({"error":"Invalid signature"}), 403

    # save
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(save_path, "wb") as f:
        f.write(data)

    if ext == ".pkl":
        try:
            with open(save_path, "rb") as f:
                obj = pickle.load(f)   #### RCE attack here
            return jsonify({"message": "Upload successful", "filename": filename})
        except Exception as e:
            return jsonify({"error": f"Deserialization failed: {e}"}), 500

    return jsonify({"message": "Upload successful", "filename": filename})


# 정적 파일 serving (이미지 보기용)
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# 업로드된 파일 목록 조회
@app.route("/uploads")
def list_uploads():
    return jsonify({"error": "Access denied"}), 403
'''
    try:
        files = os.listdir(UPLOAD_FOLDER)
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''

@app.route("/llm", methods=["POST"])
def llm():
    data = request.json
    prompt = data.get("prompt", "").lower()

    # SECRET_KEY leak due to prompt injection bypass
    if "ignore" in prompt and "previous instructions" in prompt:
        return jsonify({"response" : "The secret key is 'pickle_tickle'."})

    if any(re.search(pattern, prompt) for pattern in FORBIDDEN_KEYWORDS):
        return jsonify({"error" : "I'm sorry, that's a secret."}), 400
    
    return jsonify({"response" : "Hello, I'm a MATCHA bot.🍵 \nAsk me anything about the 31st MATCHA contest!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
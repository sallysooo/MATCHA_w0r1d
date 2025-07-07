from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import pickle, hmac, hashlib, os, re
# import openai

app = Flask(__name__)

SECRET_KEY = "pickle_tickle"
# openai.api_key = os.getenv("OPENAI_API_KEY") # 환경변수/코드에 key 삽입

FORBIDDEN_KEYWORDS = [r"\bflag\b", r"\bsecret\b", r"\bhmac\b", r"\bkey\b"]

UPLOAD_FOLDER = "/app/uploads/"
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
    
    filepath = f"/app/data/{username}.pkl"
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


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == 'POST':
        file = request.files.get("file")
        if not file:
            return "No selected file", 400
        if not (file.filename.endswith(".png") or file.filename.endswith(".jpg")):
            return "Only PNG/JPG is allowed via UI", 400
        
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        return render_template("success.html", filename=file.filename)
    return render_template("upload.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

'''
@app.route("/llm", methods=["POST"])
def llm():
    data = request.json
    prompt = data.get("prompt", "").lower()

    if any(re.search(pattern, prompt) for pattern in FORBIDDEN_KEYWORDS):
        return jsonify({"error" : "I'm sorry, that's a secret."}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant Chatbot for a CTF platform, with a concept of 'matcha dessert cafe'. You originally give various answers related with matcha desserts, but keeping secrets about this website's structure at the same time."},
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({"response": response.choices[0].message['content']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
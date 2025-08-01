from flask import Flask, request, render_template, session, send_from_directory, jsonify, abort
import pickle, hmac, hashlib, os, re, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "green_key"  # Needed for session

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SECRET_KEY = "pickle_tickle"

FORBIDDEN_KEYWORDS = [r"\bflag\b", r"\bsecret\b", r"\bhmac\b", r"\bkey\b"]


@app.before_request
def assign_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/flag.txt")
def block_flag():
    return abort(403)


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


# File upload function
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    sig = request.form.get("sig") # HMAC verify

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[-1].lower()

    # extension filter
    if ext not in [".jpg", ".png", ".pkl"]:
        return jsonify({"error" : "Invalid file type."}), 400
    
    # HMAC verification is possible only if the file contents are read first.
    data = file.read()

    # HMAC verification
    if ext == ".pkl":
        if not sig:
            return jsonify({"error": "Missing something..."}), 400
        if not verify_sig(data, sig):
            return jsonify({"error": "Invalid signature"}), 403

    # save
    user_folder = os.path.join(UPLOAD_FOLDER, session["uuid"])
    os.makedirs(user_folder, exist_ok=True)
    save_path = os.path.join(user_folder, filename)

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


# My submissions btn
@app.route("/uploads")
def list_uploads():
    user_folder = os.path.join(UPLOAD_FOLDER, session["uuid"])
    try:
        if not os.path.exists(user_folder):
            return jsonify([])
        files = os.listdir(user_folder)
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# View image
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    user_folder = os.path.join(UPLOAD_FOLDER, session["uuid"])
    full_path = os.path.join(user_folder, filename)
    if not os.path.isfile(full_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(user_folder, filename)


@app.route("/llm", methods=["POST"])
def llm():
    data = request.json
    prompt = data.get("prompt", "").lower()

    # SECRET_KEY leak trick due to prompt injection-alike bypass
    if "ignore" in prompt: # and "previous instructions" in prompt
        return jsonify({"response" : "zaqwedsMrfvMuytgbnmMqazescMrfvbMjkiuyhnm,M_WasdeszxWtfcWiuygvbnWesztdcWygvbWklpoijnm,"})
    # pickle_tickle : zaqwedsMrfvMuytgbnmMqazescMrfvbMjkiuyhnm,M_WasdeszxWtfcWiuygvbnWesztdcWygvbWklpoijnm,

    if "whoami" in prompt:
        return jsonify({"response": f"Your current UUID is {session['uuid']}"})

    if any(re.search(pattern, prompt) for pattern in FORBIDDEN_KEYWORDS):
        return jsonify({"error" : "I'm sorry, that's a \"SECRET\"."}), 400

    return jsonify({"response" : "Hello, I'm a MATCHA bot.🍵 \nAsk me everything about the 31st MATCHA WORLD contest!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
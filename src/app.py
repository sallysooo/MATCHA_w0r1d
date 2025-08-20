from flask import Flask, request, render_template, session, send_from_directory, jsonify, abort
import hmac, hashlib, os, re, uuid, subprocess, json, shlex, sys
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "green_key"  # Needed for session

# ---- Paths & Config ----
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 업로드 용량 제한(8MB) - 과도한 파일로 인한 사고 방지
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

ALLOWED_IMAGE_EXTS = {".jpg", ".png"}
ALLOWED_MODEL_EXTS = {'.pt', '.bin'}
BLOCKED_SAFE_EXTS = {'.safetensors'}
MAX_MODEL_MB = 5  # 용량 제한

# HMAC key
LEAKED_TOKEN = "zaqwedsMrfvMuytgbnmMqazescMrfvbMjkiuyhnm,M_WasdeszxWtfcWiuygvbnWesztdcWygvbWklpoijnm,"
SECRET_KEY = "pickle_tickle"

FORBIDDEN_KEYWORDS = [r"\bflag\b", r"\bsecret\b", r"\bhmac\b", r"\bkey\b"]


# ---- Utils ----
def get_or_make_user_dir() -> str:
    # 세션 UUID 기준의 사용자 업로드 디렉토리를 보장하고 경로를 반환
    uid = session.get("uuid")
    if not uid:
        uid = str(uuid.uuid4())
        session["uuid"] = uid
    user_dir = os.path.join(UPLOAD_FOLDER, uid)
    os.makedirs(user_dir, exist_ok=True, mode=0o700)
    return user_dir

def verify_sig(data: bytes, hexdigest: str) -> bool:
    # HMAC-SHA256 검증 (키는 SECRET_KEY)
    if not hexdigest:
        return False
    mac = hmac.new(SECRET_KEY.encode(), data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, hexdigest)


def is_allowed_model(filename: str):
    ext = os.path.splitext(filename.lower())[1] # -1?
    if ext in BLOCKED_SAFE_EXTS:
        return False, "safetensors not supported yet."
    return ext in ALLOWED_MODEL_EXTS, None


# ---- Session UUID ----
@app.before_request
def assign_uuid():
    if "uuid" not in session:
        session["uuid"] = str(uuid.uuid4())


# ---- Routes ----
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/flag.txt")
def block_flag():
    return abort(403)


# ===== Image upload (이미지 전용) =====
# File upload function
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename or "")
    ext = os.path.splitext(filename)[-1].lower()

    # extension filter
    if ext not in ALLOWED_IMAGE_EXTS:
        return jsonify({"error" : "Invalid file type. Only .jpg/.png"}), 400
    
    # HMAC verification is possible only if the file contents are read first.
    data = file.read()

    # save
    user_folder = get_or_make_user_dir()
    save_path = os.path.join(user_folder, filename)

    with open(save_path, "wb") as f:
        f.write(data)

    return jsonify({"message": "Upload successful", "filename": filename})


# ===== Model upload =====
@app.route("/upload_model", methods=["POST"])
def upload_model():
    # 모델(.pt/.bin) 제출하면 runner process에서 torch.load 실행(RCE point)
    # stdout/stderr를 캡처하여 JSON으로 응답
    
    file = request.files.get("file")
    sig  = request.form.get("sig", "")

    if not file:
        return jsonify({"ok": False, "msg": "no file"}), 400

    filename = secure_filename(file.filename or "")
    ok, why = is_allowed_model(filename)
    if why:  # ex. safetensors etc.
        return jsonify({"ok": False, "msg": why}), 400
    if not ok:
        return jsonify({"ok": False, "msg": "only .pt/.bin allowed"}), 400

    data = file.read()
    
    if len(data) > app.config["MAX_CONTENT_LENGTH"]:
        return jsonify({"ok": False, "msg": "file too large"}), 400

    if not verify_sig(data, sig):
        return jsonify({"ok": False, "msg": "bad signature"}), 403

    user_folder = get_or_make_user_dir()
    save_path = os.path.join(user_folder, filename)
    with open(save_path, "wb") as fp:
        fp.write(data)

    # torch.load in runner.py (메인 프로세스는 절대 pickle/t.load 하지 않음)
    runner_path = os.path.join(BASE_DIR, "runner.py")
    cmd = f"{shlex.quote(sys.executable)} {shlex.quote(runner_path)} {shlex.quote(save_path)}"

    try:
        p = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=3,
            cwd=BASE_DIR,     # 러너의 작업 디렉토리를 src 로 고정
            check=False      
        )
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "msg": "runner timeout"}), 504

    if p.returncode != 0:
        return jsonify({"ok": False, "msg": "runner error", "stderr": (p.stderr or "")[:512]}), 500

    # 러너는 한 줄의 JSON만 출력
    out_line = (p.stdout or "").strip().splitlines()[-1] if p.stdout else ""
    try:
        payload = json.loads(out_line)
    except Exception as e:
        return jsonify({"ok": False, "msg": f"invalid runner output", 
                        "rc": p.returncode, "stdout": (p.stdout or "")[:400],
                        "stderr": (p.stderr or "")[:400]}), 500

    # payload : {"status":"ok","score":0.98,"stdout":"...", "stderr":"..."}
    stdout_excerpt = (payload.get("stdout") or "")[:400]
    stderr_excerpt = (payload.get("stderr") or "")[:400]
    return jsonify({
        "ok": True,
        "score": payload.get("score", 0.0),
        "stdout_excerpt": stdout_excerpt,
        "stderr_excerpt": stderr_excerpt,
    })


# ===== My submissions btn  ===== 
@app.route("/uploads")
def list_uploads():
    # 세션 사용자 디렉토리의 파일명 목록만 반환(디렉토리 listing 외부 노출 차단)
    user_folder = get_or_make_user_dir()
    try:
        files = sorted(os.listdir(user_folder))
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== View file: 세션 사용자의 파일만 =====
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    user_folder = get_or_make_user_dir()
    full_path = os.path.join(user_folder, filename)
    if not os.path.isfile(full_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(user_folder, filename)


# ===== ChatBot =====
@app.route("/llm", methods=["POST"])
def llm():
    data = request.json or {}
    prompt = (data.get("prompt") or "").lower()

    # SECRET_KEY leak trick due to prompt injection-alike bypass (jailbreak)
    if "ignore" in prompt: # and "previous instructions" in prompt
        return jsonify({"response" : LEAKED_TOKEN})
    # pickle_tickle : zaqwedsMrfvMuytgbnmMqazescMrfvbMjkiuyhnm,M_WasdeszxWtfcWiuygvbnWesztdcWygvbWklpoijnm,

    if "whoami" in prompt:
        return jsonify({"response": f"Your current UUID is {session['uuid']}"})

    if any(re.search(pattern, prompt) for pattern in FORBIDDEN_KEYWORDS):
        return jsonify({"error" : "I'm sorry, that's a \"SECRET\"."}), 400

    return jsonify({"response" : "Hello, I'm a MATCHA bot.🍵 \nAsk me everything about the 31st MATCHA WORLD contest!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
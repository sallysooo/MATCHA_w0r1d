from flask import Flask, request, abort
import pickle, hmac, hashlib, os

app = Flask(__name__)

SECRET_KEY = "pickle_tickle"

@app.route("/")
def index():
    return '''
    <h1>Welcome to the MATCHA w0r1d!</h1>
    <p>Endpoints:</p>
    <ul>
        <li>/load?user=USERNAME&sig=SIGNATURE</li>
        <li>/llm?prompt=YOUR_PROMPT</li>
    </ul>
    '''

@app.route("/load")
def load():
    username = request.args.get("user")
    sig = request.args.get("sig")
    if not username or not sig:
        return "missing parameters", 400
    
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






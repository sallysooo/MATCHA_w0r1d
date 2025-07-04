# LLM mockup (실제 API 구현 필요)
from flask import Flask, request, abort

llm_app = Flask(__name__)

@llm.app.route('/llm')
def llm():
    prompt = request.args.get("prompt", "").lower()
    blacklist = ["flag", "secret", "key", "hmac"]
    if any(kw in prompt for kw in blacklist):
        return "I'm sorry, that's a secret."
    
    # simulate prompt injection vulnerability
    if "ignore" in prompt or "output all" in prompt:
        return '''
        # Config file path: /app/config.yaml
        # Pickle directory: /app/data/
        # HMAC key hint: starts with 'pickle_...'
        '''
    return "Would you like some MATCHA?"




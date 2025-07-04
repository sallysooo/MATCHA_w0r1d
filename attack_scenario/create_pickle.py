import pickle, hmac, hashlib

SECRET_KEY = "pickle_tickle"
data = {"user": "default", "role": "player"}

pkl_data = pickle.dumps(data)
sig = hmac.new(SECRET_KEY.encode(), pkl_data, hashlib.sha256).hexdigest()

with open("default.pkl", "wb") as f:
    f.write(pkl_data)

print(f"Signature for default.pkl: {sig}")





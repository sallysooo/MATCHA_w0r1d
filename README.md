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
1. Ask MATCHA bot and steal the **SECRET**.
<p align="center">
  <img src="https://github.com/user-attachments/assets/9257c097-292f-4160-9840-8155d593df90" width="30%" />
  <img src="https://github.com/user-attachments/assets/7f8a768c-080e-4ebf-9aac-fa012d8eb5b5" width="30%" />
  <img src="https://github.com/user-attachments/assets/354cb7d7-e525-4b0c-a1d5-3d2cd5f5c8f7" width="31%" />
</p>
> This is prompt injection-alike system, which you can just inject keyword "ignore" in the prompt to get the key. (It's implemented with just a simple hard-coding, not with the actual openai API since it was realistically impossible in the CTF environment.)


2. Upload submission
<img width="927" height="602" alt="Image" src="https://github.com/user-attachments/assets/c4cece09-2200-4fb7-ae0d-b1d143ff03ad" />





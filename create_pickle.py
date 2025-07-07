import pickle, hmac, hashlib

SECRET_KEY = "pickle_tickle"
data = {"user": "default", "role": "matcha_lover"}

pkl_data = pickle.dumps(data)  # 1. dict 객체를 직렬화 
# HMAC = pickle 데이터가 변조되지 않았음을 증명 
# 서버가 pickle 데이터를 로드하기 전에 이 sig를 검증하며, sig가 맞지 않으면 invalid signature
sig = hmac.new(SECRET_KEY.encode(), pkl_data, hashlib.sha256).hexdigest() # 2. data에 대해 HMAC signature 생성 : 919e4dd...

with open("app/data/default.pkl", "wb") as f:
    f.write(pkl_data)

print(f"Valid signature for default.pkl: {sig}")


# Valid signature for default.pkl: 919e4ddde922d4aeeebe369409a5e40306ed421dee3ea86653e1d121ffb20c68
# 최종 RCE의 표적 : flag.txt
'''
<참가자에게 공개된 endpoint>
/load?user=default&sig=919e4dd...(정상 url) -> 이걸 보고 추론하는 것
/load?user=<다른 값>&sig=<직접 만든 sig>(참가자가 도전)

- pickle 취약점의 핵심: pickle.loads()는 단순 데이터 복원이 아니라, 코드를 실행할 수 있는 동작까지 포함
- pickle 데이터 내부에 "이 객체를 복원할 때 이 함수를 실행하라" 같은 명령을 담을 수 있고, 이게 바로 deserialization 취약점!

<참가자의 공격 scenario>
1. 공격용 pickle 생성 -> os.system("cat /flag")같은 RCE payload 삽입
2. 생성한 pickle에 대해 valid HMAC sig 생성 -> 이를 토대로 /load?user=malicious&sig=...로 호출 
3. 서버가 pickle.loads()로 이 데이터를 deserialization 하도록 유도
4. 서버에서 명령어 실행 -> flag 출력


'''
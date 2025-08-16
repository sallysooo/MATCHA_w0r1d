import sys, io, json, contextlib, random
import torch  # CPU 전용 설치

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"status": "err", "msg": "usage"}))
        sys.exit(2)

    path = sys.argv[1]
    out = io.StringIO()
    err = io.StringIO()

    # 로드 중 생성되는 stdout/stderr를 모두 캡처
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        # 의도적으로 위험한 로드 (weights_only=False 기본)
        obj = torch.load(path, map_location="cpu")

    # 그럴듯한 가짜 스코어
    score = random.uniform(0.73, 1.00)
    decimal_places = random.randint(2, 6)
    score = round(score, decimal_places) # 0.84, 0.736, 0.9385, ...

    print(json.dumps({
        "status": "ok",
        "score": score,
        "stdout": out.getvalue(),
        "stderr": err.getvalue()
    }))

if __name__ == "__main__":
    main()

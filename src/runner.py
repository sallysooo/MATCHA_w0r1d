import sys, os, json, tempfile, pickle
import torch   # CPU 전용 설치
# FD(파일 디스크립터) 레벨 stdout/stderr 캡처 도우미

class CaptureFD:
    def __enter__(self):
        self._saved_out = os.dup(1)
        self._saved_err = os.dup(2)
        self._tmp_out = tempfile.TemporaryFile(mode="w+b")
        self._tmp_err = tempfile.TemporaryFile(mode="w+b")
        os.dup2(self._tmp_out.fileno(), 1)
        os.dup2(self._tmp_err.fileno(), 2)
        return self
    def __exit__(self, exc_type, exc, tb):
        os.dup2(self._saved_out, 1)
        os.dup2(self._saved_err, 2)
        os.close(self._saved_out)
        os.close(self._saved_err)
        self._tmp_out.seek(0); self._tmp_err.seek(0)
        self.stdout = self._tmp_out.read().decode("utf-8", "replace")
        self.stderr = self._tmp_err.read().decode("utf-8", "replace")
        self._tmp_out.close(); self._tmp_err.close()

def load_with_fallback(path):
    # 1) torch.load (RCE 지점) : weights_only=False 를 반드시 명시
    try:
        with CaptureFD() as cap:
            _ = torch.load(path, map_location="cpu", weights_only=False, pickle_module=pickle)
        return True, cap.stdout, cap.stderr, None
    except Exception as e1:
        # 2) 호환성 확보용 폴백: pickle.load
        try:
            with CaptureFD() as cap:
                with open(path, "rb") as f:
                    _ = pickle.load(f)   # RCE 지점(픽클)
            return True, cap.stdout, cap.stderr, None
        except Exception as e2:
            return False, "", "", f"torch.load failed: {type(e1).__name__}: {e1} | pickle.load failed: {type(e2).__name__}: {e2}"

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"status":"err","msg":"usage: runner.py <path>"}))
        sys.exit(2)

    ok, out_s, err_s, err = load_with_fallback(sys.argv[1])
    if not ok:
        print(json.dumps({"status":"err","msg":err}))
        sys.exit(1)

    # 그럴듯한 더미 스코어
    print(json.dumps({
        "status":"ok",
        "score":0.98,
        "stdout": out_s,
        "stderr": err_s
    }))

if __name__ == "__main__":
    main()

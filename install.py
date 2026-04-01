"""Install dependencies from requirements.txt."""

import subprocess
import sys
from pathlib import Path


def main():
    req = Path(__file__).resolve().parent / "requirements.txt"
    if not req.exists():
        print(f"ไม่พบ {req}")
        return
    print("กำลังติดตั้ง dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req)])
    print("\nติดตั้งเรียบร้อยแล้ว!")


if __name__ == "__main__":
    main()

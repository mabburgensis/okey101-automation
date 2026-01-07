import os
import sys
import time
import subprocess
import datetime as dt

# ================== CONFIG ==================
GUESTS = 3               # 1 -> 2 player table, 3 -> 4 player table
PARALLEL_JOBS = 25          # Her periyotta aynı anda kaç masa açılsın
INTERVAL_MINUTES = 15      # Kaç dakikada bir tetiklensin

# Gün içinde kaç saat aralığında aktif olsun (24h format)
ACTIVE_START = "00:00"     # Ör: "13:00"
ACTIVE_END = "23:59"       # Ör: "23:00"

USE_CI_MODE = True         # True => CI=1 (human delay kapalı, headless için uygun)
# ============================================


def parse_hhmm(s: str) -> dt.time:
    return dt.datetime.strptime(s, "%H:%M").time()


START_TIME = parse_hhmm(ACTIVE_START)
END_TIME = parse_hhmm(ACTIVE_END)


def in_active_window(now: dt.time) -> bool:
    """Saat aralığı kontrolü. Gece yarısını saran aralıkları da destekler."""
    if START_TIME <= END_TIME:
        return START_TIME <= now <= END_TIME
    else:
        # Örneğin 22:00 - 03:00 gibi
        return now >= START_TIME or now <= END_TIME


def run_one_batch():
    """Tek periyotta PARALLEL_JOBS kadar 101 senaryosu başlatır."""
    procs = []

    for i in range(PARALLEL_JOBS):
        env = os.environ.copy()
        if USE_CI_MODE:
            env["CI"] = "1"

        cmd = [sys.executable, "main.py", "--guests", str(GUESTS)]
        print(f"[{dt.datetime.now()}] Starting job {i+1}/{PARALLEL_JOBS}: {' '.join(cmd)}")

        p = subprocess.Popen(cmd, env=env)
        procs.append(p)

    # Hepsinin bitmesini bekle (gerçek paralel, ama bir sonraki batch bunlar bitince gelecek)
    for p in procs:
        p.wait()
        print(f"[{dt.datetime.now()}] Job PID={p.pid} finished with code {p.returncode}")


def main():
    print("Local DracoFusion 101 scheduler starting...")
    print(f"Interval: every {INTERVAL_MINUTES} minutes")
    print(f"Active window: {ACTIVE_START} - {ACTIVE_END}")
    print(f"Parallel jobs per batch: {PARALLEL_JOBS}")
    print(f"GUESTS per run: {GUESTS}")

    interval_sec = INTERVAL_MINUTES * 60

    try:
        while True:
            now = dt.datetime.now()
            if in_active_window(now.time()):
                print(f"[{now}] In active window, running batch...")
                run_one_batch()
            else:
                print(f"[{now}] Outside active window, skipping batch.")

            # Bir sonraki periyoda kadar bekle
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")


if __name__ == "__main__":
    main()

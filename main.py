# main.py
import subprocess
import os
import argparse
import sys

TEST_FILES = [
    ("101.py",     True),   # 101.py mutlaka --guests bekliyor
]


def run_test(file_name: str, pass_guests: bool, guests: int):
    print(f"\nTest starting: {file_name}")

    cmd = ["python", file_name]
    if pass_guests:
        cmd += ["--guests", str(guests)]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Test failed: {file_name} (exit code: {result.returncode})")
        print("Test chain stopped.")
        sys.exit(1)
    else:
        print(f"Test finished successfully: {file_name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automation Test Runner (main.py) – runs register, login and 101 flows."
    )
    parser.add_argument(
        "--guests",
        type=int,
        required=True,
        help="Number of guest players for 101.py (must be 1 or 3). Total players = 1 host + guests.",
    )
    args = parser.parse_args()

    if args.guests not in (1, 3):
        print(
            f"INFO | Invalid --guests value: {args.guests}. "
            "It must be 1 or 3 (1 host + guests = 2 or 4 players)."
        )
        sys.exit(1)

    return args


if __name__ == "__main__":
    args = parse_args()
    guests = args.guests

    print("=== Automation Test Runner (main.py) ===")
    print(f"INFO | Guests parameter will be passed to 101.py: --guests {guests}\n")

    for file_name, needs_guests in TEST_FILES:
        if os.path.exists(file_name):
            run_test(file_name, needs_guests, guests)
        else:
            print(f"File not found: {file_name}")

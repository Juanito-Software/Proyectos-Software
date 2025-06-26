# progress_bar_utils.py

import sys

def show_basic_progress_bar(progress, total):
    bar_length = 50
    filled_length = int(progress / total * bar_length)
    bar = "[" + "=" * filled_length + " " * (bar_length - filled_length) + "]"
    sys.stdout.write(f"\r{bar} {progress}/{total}")
    sys.stdout.flush()

def show_fancy_progress_bar(progress, total):
    bar_length = 50
    filled_length = int(progress / total * bar_length)
    percent = int(progress / total * 100)
    spinner = ['|', '/', '-', '\\']
    bar = "[" + "=" * filled_length + " " * (bar_length - filled_length) + "]"
    sys.stdout.write(f"\r{bar} {percent}% {spinner[progress % len(spinner)]}")
    sys.stdout.flush()

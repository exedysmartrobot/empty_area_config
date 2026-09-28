import subprocess
import os
import json
from pathlib import Path

MANAGER_DIR = Path(__file__).resolve().parent


def load_json(filename):
    file_path = MANAGER_DIR / filename
    with open(file_path, "r",  encoding="utf-8") as file:
        return json.load(file)


def save_json(filename, data):
    """MANAGER_DIR 内の指定したファイル名でデータを保存する"""
    file_path = MANAGER_DIR / filename
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def play_audio(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    media_dir = os.path.join(base_dir, "static", "media")
    mp3_path = os.path.join(media_dir, filename)
    # print(f"📢 再生中: {mp3_path}")
    subprocess.run(['play', '-q', mp3_path])

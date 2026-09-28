#!/usr/bin/env python3
# coding: utf-8
"""
Frame Designer — Flask 版の土台

今は index.html をそのまま配信するだけ。
Python 側でやりたいことが決まったら、下の「拡張ポイント」に
ルートを足していく想定。

"""

import os

from dotenv import load_dotenv
from flask import Flask, Response, render_template, jsonify, request, send_from_directory

from app_client import main_api_client, get_route_list

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

ROBOT_ID = os.getenv("ROBOT_ID")

app = Flask(__name__)

# BASIC_AUTH_USER / BASIC_AUTH_PASSWORD が設定されている時だけBasic認証をかける
# （Render等で公開する時用。ローカルでは未設定のままでOK）
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")


@app.before_request
def require_basic_auth():
    if not (BASIC_AUTH_USER and BASIC_AUTH_PASSWORD):
        return None
    auth = request.authorization
    if auth and auth.username == BASIC_AUTH_USER and auth.password == BASIC_AUTH_PASSWORD:
        return None
    return Response("Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Frame Designer"'})


# ====================== 画面 ======================

@app.route("/")
def index():
    """ツール本体（既存の index.html）を返す。"""
    return render_template("index.html")


# ====================== 動作確認用 ======================

@app.route("/api/ping")
def ping():
    """疎通確認。ブラウザから fetch('/api/ping') で {'ok': true} が返る。"""
    return jsonify({"ok": True, "message": "flask is running"})


# ====================== ロボット現在地 ======================

@app.route("/api/robot_pose")
def get_robot_pose():
    """ロボットの現在位置(マップ画像と同じpx座標系)を取得して返す。"""
    if not ROBOT_ID:
        return jsonify({"ok": False, "error": "ROBOT_ID is not configured"}), 500

    response = main_api_client(ROBOT_ID, "get_pose", {}) or {}
    pose = response.get("pose")
    if not pose:
        error = response.get("error") or f"status: {response.get('status')}"
        return jsonify({"ok": False, "error": error}), 502

    return jsonify({
        "ok": True,
        "pose": {"x": pose.get("x"), "y": pose.get("y"), "angle": pose.get("angle")},
    })


@app.route("/api/robot_map")
def get_robot_map():
    """ロボットの現在のマップ画像を取得して返す。"""
    if not ROBOT_ID:
        return jsonify({"ok": False, "error": "ROBOT_ID is not configured"}), 500

    response = main_api_client(ROBOT_ID, "get_map", {}) or {}
    map_data = response.get("map")
    if not map_data:
        error = response.get("error") or f"status: {response.get('status')}"
        return jsonify({"ok": False, "error": error}), 502

    return jsonify({"ok": True, "map": map_data})


@app.route("/api/route_list")
def get_robot_route_list():
    """現在のマップに登録されているルート一覧(名前+経路のpx座標)を取得して返す。"""
    if not ROBOT_ID:
        return jsonify({"ok": False, "error": "ROBOT_ID is not configured"}), 500

    map_id_response = main_api_client(ROBOT_ID, "get_map_id", {}) or {}
    map_id = map_id_response.get("map_id")
    if not map_id:
        error = map_id_response.get("error") or f"status: {map_id_response.get('status')}"
        return jsonify({"ok": False, "error": error}), 502

    routes = get_route_list(map_id)
    return jsonify({"ok": True, "routes": routes})


# ====================== 拡張ポイント（未実装のひな形） ======================
# やりたいことが決まったら、以下のコメントを外して中身を書く。

# --- 設定(YAML/JSON)をサーバーに保存・読込したい場合 ---
#
# import yaml
#
# @app.route("/api/config", methods=["POST"])
# def save_config():
#     data = request.get_json()          # ブラウザから送られてきた枠データ
#     path = os.path.join(CONFIG_DIR, "frame_config.yaml")
#     with open(path, "w") as f:
#         yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
#     return jsonify({"ok": True, "path": path})
#
# @app.route("/api/config", methods=["GET"])
# def load_config():
#     path = os.path.join(CONFIG_DIR, "frame_config.yaml")
#     if not os.path.exists(path):
#         return jsonify({"ok": False, "error": "not found"}), 404
#     with open(path) as f:
#         data = yaml.safe_load(f)
#     return jsonify({"ok": True, "config": data})


# --- マップ画像を Python 経由で取得したい場合（CORS 回避の中継） ---
#
# import requests   # pip install requests
#
# @app.route("/api/map")
# def get_map():
#     # ここで外部APIを Python 側から叩いて、画像やURLをブラウザに返す
#     # （ブラウザの CORS 制約を受けずに済む）
#     ...


# --- ROS と連携したい場合 ---
#
# ここに rospy を使った publish などを足す。
# （ROS 環境の Python で動かす必要がある点に注意）


# ====================== 静的ファイル ======================

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)


if __name__ == "__main__":
    # debug=True は開発用（保存すると自動リロード）
    app.run(host="0.0.0.0", port=5000, debug=True)

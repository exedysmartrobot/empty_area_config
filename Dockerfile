# module/RobotControl.pyc が Python 3.8 でコンパイルされているため 3.8 固定
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render は PORT 環境変数で待ち受けポートを渡してくる
# ロボットAPIのポーリングが長引くことがあるので timeout を長めに取る
CMD gunicorn server:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 4 --timeout 180

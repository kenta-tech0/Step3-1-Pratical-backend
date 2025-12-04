from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SSL_CA_PATH = os.getenv('SSL_CA_PATH')

# SSL証明書ファイルのパスを絶対パスに変換
if SSL_CA_PATH:
    if not os.path.isabs(SSL_CA_PATH):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        cert_path = os.path.join(backend_dir, SSL_CA_PATH)
    else:
        cert_path = SSL_CA_PATH
else:
    raise ValueError("SSL_CA_PATH環境変数が設定されていません")

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "ssl": {
            "ca": cert_path,
            "check_hostname": True,  # 本番環境推奨
            "verify_mode": "CERT_REQUIRED"  # 証明書検証を必須に
        }
})
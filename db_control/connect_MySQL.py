from sqlalchemy import create_engine

import os
import tempfile
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

# SSL証明書の処理
cert_path = None
if SSL_CA_PATH:
    # SSL_CA_PATHが証明書の内容（PEM形式）かファイルパスかを判定
    if SSL_CA_PATH.startswith('-----BEGIN CERTIFICATE-----'):
        # 証明書の内容が直接環境変数に格納されている場合
        # リテラル文字列 '\n' を実際の改行文字に変換
        cert_content = SSL_CA_PATH.replace('\\n', '\n')
        # 一時ファイルに書き込む
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as cert_file:
            cert_file.write(cert_content)
            cert_path = cert_file.name
    elif os.path.exists(SSL_CA_PATH):
        # 既存のファイルパスの場合
        cert_path = SSL_CA_PATH
    elif not os.path.isabs(SSL_CA_PATH):
        # 相対パスの場合、絶対パスに変換
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        potential_path = os.path.join(backend_dir, SSL_CA_PATH)
        if os.path.exists(potential_path):
            cert_path = potential_path

# エンジンの作成
# SSL証明書が設定されている場合のみSSL接続を使用
if cert_path:
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "ssl": {
                "ca": cert_path,
                "check_hostname": True,
                "verify_mode": "CERT_REQUIRED"
            }
        }
    )
else:
    # SSL証明書が設定されていない場合、SSLなしで接続
    # または Azure MySQL Flexible Server の場合はシステムのCA証明書を使用
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "ssl": {
                "check_hostname": False,
                "verify_mode": "CERT_NONE"
            }
        }
    )

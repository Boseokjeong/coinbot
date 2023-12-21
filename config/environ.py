import os
from dotenv import load_dotenv

load_dotenv()


class Environ:

    # 장고 시크릿 키
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # RDS 정보
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_NAME = os.environ.get('DB_NAME')

    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_PORT = os.environ.get('REDIS_PORT')

    UPBIT_ACCESS_KEY = os.environ.get('UPBIT_ACCESS_KEY')
    UPBIT_SECRET_KEY = os.environ.get('UPBIT_SECRET_KEY')


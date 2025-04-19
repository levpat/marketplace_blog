import os
import dotenv
from passlib.context import CryptContext

dotenv.load_dotenv()
db_url = os.getenv('DB_URL')
host = os.getenv('HOST')
port = int(os.getenv('PORT'))
secret_key = os.getenv('SECRET_KEY')
alg = os.getenv('ALG')
mail_address = os.getenv('MAIL_ADDRESS_FOR_GOOGLE')
mail_pass = os.getenv('MAIL_PASS_FOR_GOOGLE')
smtp = os.getenv('SMTP_2')
minio_access = os.getenv('MINIO_ACCESS_KEY')
minio_secret = os.getenv('MINIO_SECRET_KEY')
minio_url = os.getenv('MINIO_URL')
minio_bucket = os.getenv('MINIO_BUCKET')
redis_url = os.getenv('BROKER')

mail_yandex = os.getenv('MAIL_ADDRESS')
pass_yandex = os.getenv('YANDEX_PASS')
smtp_ya = os.getenv('SMTP')

valid_exceptions = {'.png', '.jpg', '.jpeg', '.pdf'}
access_token_expire_minutes = 20
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

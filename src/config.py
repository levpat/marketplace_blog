import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv('DB_URL')

host = os.getenv('HOST')
port = int(os.getenv('PORT'))

secret = os.getenv("SECRET_KEY")
alg = os.getenv("ALGORITHM")

mail_pass = os.getenv('MAIL_PASS')
smtp = os.getenv("SMTP")
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv('DB_URL')

host = os.getenv('HOST')
port = int(os.getenv('PORT'))

secret = os.getenv("SECRET_KEY")
alg = os.getenv("ALGORITHM")

mail_address = os.getenv("MAIL_ADDRESS")
mail_pass = os.getenv('MAIL_PASS')
smtp = os.getenv("SMTP")

mail_address_2 = os.getenv("MAIL_ADDRESS_FOR_GOOGLE")
mail_pass_for_google = os.getenv("MAIL_PASS_FOR_GOOGLE")
smtp_google = os.getenv("SMTP_2")


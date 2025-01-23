from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:h27ynCKXMAYr@localhost/db_pncp')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

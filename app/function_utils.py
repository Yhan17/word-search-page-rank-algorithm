import pymysql
from pydantic import BaseModel

DB_HOST="mysql"
DB_USERNAME="root"
DB_PASSWORD="123456"
DB_NAME="indice"
DB_PORT=3306

connection = pymysql.connect(
  host= DB_HOST,
  user=DB_USERNAME,
  passwd= DB_PASSWORD,
  db= DB_NAME,
  port=DB_PORT,
  autocommit= True,
  use_unicode=True,
  charset='utf8mb4'
)


class Payload(BaseModel):
    words: str
    frequence_weight: float = 1.0
    localization_weight: float = 1.0
    distance_weight: float = 1.0
    count_weight: float = 5.0
    page_rank_weight: float = 1.0
    text_link_weight: float = 1.0

async def connect_to_db():

  try:
    cursor = connection.cursor()
    cursor.execute('select 1')

    return 'DATABASE CONNECTED'
  except Exception as e:
    print('Database not connected')
    print(e)
    return ''


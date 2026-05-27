import urllib
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- 1. COLOQUE SUAS CREDENCIAIS DO AZURE AQUI ---
SERVER = 'gondoled003.database.windows.net'
DATABASE = 'scf_monitoramento_rodoviario'
USERNAME = 'CloudSAed5e5704'
PASSWORD = 'Gondoled2026@'

# O driver padrão utilizado pelo Azure. 
# Se der erro no Windows localmente, tente mudar para 'ODBC Driver 17 for SQL Server'
DRIVER = 'ODBC Driver 17 for SQL Server'

# --- 2. MONTAGEM DA STRING DE CONEXÃO ---
# Usamos urllib para codificar a senha, evitando erros caso ela tenha caracteres especiais (@, #, !, etc)
params = urllib.parse.quote_plus(
    f"DRIVER={{{DRIVER}}};SERVER={SERVER};PORT=1433;DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)

# Essa é a URL no formato que o SQLAlchemy entende para o SQL Server
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
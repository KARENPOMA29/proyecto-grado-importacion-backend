from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 📌 Configuración directa de la base de datos
DB_USER = "sa"
DB_PASSWORD = "6707"
DB_HOST = "DESKTOP-9BLQ9SP\\SQLEXPRESS"
DB_NAME = "BDD_ImportacionSystem"

# 📡 Cadena de conexión a SQL Server
DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
)

# 🔌 Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# 🗄️ Sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🧱 Clase base para modelos ORM
Base = declarative_base()

# 🔄 Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

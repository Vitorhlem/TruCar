from sqlalchemy.orm import declarative_base

# A única responsabilidade deste ficheiro é criar e exportar a Base.
Base = declarative_base()

# A LINHA MÁGICA: Importa todos os modelos DEPOIS que a Base foi definida.
# Isto garante que a Base já conhece todas as suas tabelas.
from app.models import *
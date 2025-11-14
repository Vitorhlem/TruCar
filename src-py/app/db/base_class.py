# backend/app/db/base_class.py

from sqlalchemy.orm import declarative_base

# A única responsabilidade deste ficheiro é criar e exportar a Base.
Base = declarative_base()
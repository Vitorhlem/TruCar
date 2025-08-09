from sqlalchemy.orm import declarative_base

# Cria a classe Base declarativa.
# Todos os modelos de dados da aplicação (tabelas do banco de dados)
# herdarão desta classe. Isso permite que o SQLAlchemy descubra e
# gerencie todos os nossos modelos a partir de um ponto central.
Base = declarative_base()
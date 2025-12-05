import os
import sys
from alembic.config import Config
from alembic import command

# Obtém o diretório onde este script está (src-py/pywrapper)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Obtém o diretório pai (src-py)
parent_dir = os.path.dirname(current_dir)

# Muda o diretório de trabalho para src-py para que o alembic.ini seja encontrado
os.chdir(parent_dir)

# Adiciona src-py ao sys.path para que os imports do projeto funcionem
sys.path.append(parent_dir)

def run_migrations():
    print("Iniciando migrações do banco de dados...")
    try:
        # Cria o objeto de configuração apontando para o alembic.ini (que está em src-py)
        alembic_cfg = Config("alembic.ini")
        
        # Executa o comando 'upgrade head'
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrações aplicadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()

import os
import sys
from a2wsgi import ASGIMiddleware

# Obtém o diretório onde este script está (src-py/pywrapper)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Obtém o diretório pai (src-py)
parent_dir = os.path.dirname(current_dir)

# Adiciona o diretório pai ao sys.path para que 'main' possa ser importado
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importa a aplicação FastAPI do arquivo main.py (que está em src-py)
from main import app as fastapi_app

# Cria a aplicação WSGI compatível com o Passenger do cPanel
application = ASGIMiddleware(fastapi_app)

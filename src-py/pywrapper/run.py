import uvicorn
import os
import sys

# Obtém o diretório onde este script está (src-py/pywrapper)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Obtém o diretório pai (src-py)
parent_dir = os.path.dirname(current_dir)

# Muda o diretório de trabalho para src-py
os.chdir(parent_dir)

# Adiciona src-py ao sys.path para que os imports do projeto funcionem
sys.path.append(parent_dir)

if __name__ == "__main__":
    print("Iniciando servidor Uvicorn...")
    # Inicia o servidor na porta 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

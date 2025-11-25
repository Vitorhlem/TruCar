import redis

print("Tentando conectar ao Redis/Memurai...")
try:
    # Tentamos forçar o IP 127.0.0.1 para evitar problemas com 'localhost' no Windows
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, socket_timeout=5)
    resposta = r.ping()
    print(f"SUCESSO! Resposta do Redis: {resposta}")
except Exception as e:
    print(f"FALHA: {e}")
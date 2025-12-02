# Arquivo: src-py/debug_routes.py
from main import app
from app.core.config import settings

print(f"\n🔍 PREFIXO DA API: '{settings.API_V1_STR}'")
print(f"🔍 ROTAS REGISTRADAS:")
print("-" * 60)

found_alert = False
found_login = False

for route in app.routes:
    if hasattr(route, "path"):
        print(f"➡️  {route.methods}  {route.path}")
        
        if "/alerts/alert" in route.path:
            found_alert = True
        if "/login/token" in route.path:
            found_login = True

print("-" * 60)

if not found_alert:
    print("❌ ERRO CRÍTICO: A rota de ALERTAS não foi encontrada!")
    print("   Verifique se você salvou o arquivo 'app/api.py' e se o servidor reiniciou.")
else:
    print("✅ Rota de ALERTAS encontrada!")

if not found_login:
    print("❌ ERRO CRÍTICO: A rota de LOGIN não foi encontrada!")
else:
    print("✅ Rota de LOGIN encontrada!")
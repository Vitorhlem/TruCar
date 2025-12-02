import asyncio
from app.db.session import SessionLocal
from app import crud
from sqlalchemy import select
from app.models.vehicle_model import Vehicle

async def get_valid_truck_id():
    async with SessionLocal() as db:
        # Busca o primeiro veículo do banco
        result = await db.execute(select(Vehicle))
        vehicle = result.scalars().first()
        
        if vehicle:
            print("\n" + "="*50)
            print(f"🚛 VEÍCULO ENCONTRADO!")
            print(f"MODELO: {vehicle.model}")
            print(f"PLACA: {vehicle.license_plate}")
            print(f"✅ COPIE ESTE ID PARA O SCRIPT: {vehicle.id}")
            print("="*50 + "\n")
        else:
            print("\n❌ Nenhum veículo encontrado no banco. Crie um primeiro!")

if __name__ == "__main__":
    asyncio.run(get_valid_truck_id())
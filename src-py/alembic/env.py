import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# --- INÍCIO DA CONFIGURAÇÃO TRUCAR ---

# Adiciona o diretório raiz do projeto (src-py) ao sys.path
# para que possamos importar o módulo 'app'
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Importe a Base declarativa de onde ela está no seu projeto
from app.db.base_class import Base
from app.core.config import settings

# Importe TODOS os seus modelos aqui.
# Isso é crucial para que o Alembic "veja" as tabelas.
from app.models.user_model import User
from app.models.organization_model import Organization
from app.models.vehicle_model import Vehicle
from app.models.implement_model import Implement
from app.models.journey_model import Journey
from app.models.fuel_log_model import FuelLog
from app.models.maintenance_model import MaintenanceRequest, MaintenanceComment
from app.models.document_model import Document
from app.models.vehicle_cost_model import VehicleCost
from app.models.fine_model import Fine
from app.models.client_model import Client
from app.models.freight_order_model import FreightOrder
from app.models.stop_point_model import StopPoint
from app.models.part_model import Part, InventoryItem
from app.models.inventory_transaction_model import InventoryTransaction
from app.models.vehicle_component_model import VehicleComponent
from app.models.alert_model import Alert
from app.models.notification_model import Notification
from app.models.goal_model import Goal
from app.models.achievement_model import Achievement
from app.models.location_history_model import LocationHistory
from app.models.demo_usage_model import DemoUsage

# --- CORREÇÃO (BASEADO NO SEU INPUT) ---
# Importa o modelo correto do seu tire_model.py
from app.models.tire_model import VehicleTire
# Removemos a importação de report_models.py, pois ele contém schemas Pydantic, não modelos SQLAlchemy.
# --- FIM DA CORREÇÃO ---

# Defina o target_metadata com a Base dos seus modelos
target_metadata = Base.metadata

# --- FIM DA CONFIGURAÇÃO TRUCAR ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Overwrite sqlalchemy.url with the one from settings
if settings.DATABASE_URI:
    # Convert async URI to sync URI for Alembic
    sync_uri = settings.DATABASE_URI.replace("postgresql+asyncpg://", "postgresql://")
    config.set_main_option("sqlalchemy.url", sync_uri)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    
    # Esta função usa a 'sqlalchemy.url' síncrona do alembic.ini
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
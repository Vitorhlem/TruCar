from sqlalchemy.orm import declarative_base

# A única responsabilidade deste ficheiro é criar e exportar a Base.
Base = declarative_base()

# A LINHA MÁGICA: Importa todos os modelos DEPOIS que a Base foi definida.
# Isto garante que a Base já conhece todas as suas tabelas.
# Ordem explícita para evitar erros de referência de chave estrangeira
from app.models.organization_model import Organization
from app.models.user_model import User
from app.models.vehicle_model import Vehicle
from app.models.implement_model import Implement
from app.models.part_model import Part
from app.models.client_model import Client
from app.models.freight_order_model import FreightOrder
from app.models.stop_point_model import StopPoint
from app.models.journey_model import Journey
from app.models.maintenance_model import MaintenanceRequest, MaintenanceComment
from app.models.fuel_log_model import FuelLog
from app.models.notification_model import Notification
from app.models.location_history_model import LocationHistory
from app.models.achievement_model import Achievement, UserAchievement
from app.models.inventory_transaction_model import InventoryTransaction
from app.models.document_model import Document
from app.models.goal_model import Goal
from app.models.alert_model import Alert
from app.models.vehicle_cost_model import VehicleCost
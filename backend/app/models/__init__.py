# Este arquivo transforma a pasta 'models' em um pacote Python
# e importa todos os nossos modelos para um único namespace.
# A ORDEM DOS IMPORTS É IMPORTANTE para que o SQLAlchemy entenda as relações.

# Modelos sem dependências diretas de outros modelos
from .user_model import User
from .vehicle_model import Vehicle

# Modelos que dependem dos anteriores
from .journey_model import Journey
from .location_history_model import LocationHistory
from .notification_model import Notification
from .maintenance_request_model import MaintenanceRequest, MaintenanceComment
from .fuel_log_model import FuelLog
from .organization_model import Organization
import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class UserRole(str, enum.Enum):
    """
    Define as funções (roles) possíveis para um usuário no sistema.
    Usar um Enum em vez de strings puras torna o código mais seguro,
    prevenindo erros de digitação e deixando as permissões explícitas.
    """
    MANAGER = "manager"
    DRIVER = "driver"

class User(Base):
    """
    Modelo da tabela de Usuários.
    
    Esta tabela armazenará todos os usuários que podem fazer login no sistema,
    sejam eles gestores ou motoristas.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean(), default=True)
    avatar_url = Column(String(512), nullable=True)

    # Relacionamento: Um usuário (motorista) pode ter várias viagens (journeys).
    # O 'back_populates' cria o link reverso no modelo Journey.
    journeys = relationship("Journey", back_populates="driver")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")

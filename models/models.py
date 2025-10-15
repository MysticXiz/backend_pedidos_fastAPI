from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils import ChoiceType

db = create_engine("sqlite:///./database/banco.db")
base = declarative_base()

class User(base):
    __tablename__ = "users"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, index=True, nullable=False)
    email = Column("email", String, unique=True, index=True, nullable=False)
    password = Column("password", String, nullable=False)
    active = Column("active", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, name, email, password, active=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin
 
class Order(base):

    STATUS = (
        ("PENDENTE", "Pendente"), 
        ("CANCELADO", "Cancelado"), 
        ("ENTREGUE", "Entregue")
    )
    __tablename__ = "orders"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String, ChoiceType(STATUS))
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    items = relationship("OrderItem", backref="order", cascade="all, delete")
    price = Column("price", Float, nullable=False)

    def __init__(self, user_id, status="PENDENTE",price=0):
        self.user_id = user_id
        self.price = price
        self.status = status

    def calculate_total(self):
        self.price = sum(item.price * item.amount for item in self.items)
    
class OrderItem(base):
    __tablename__ = "items"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    order_id = Column("order", Integer, ForeignKey("orders.id"))
    name = Column("name", String, nullable=False)
    description = Column("description", String)
    price = Column("price", Integer, nullable=False)
    amount = Column("amount", Integer, default=0)

    def __init__(self, name, price, order_id, description="", amount=0):
        self.name = name
        self.price = price
        self.description = description
        self.amount = amount
        self.order_id = order_id

#migration line: alembic revision --autogenerate -m "Descrição da migração" 
#migration line: alembic upgrade head
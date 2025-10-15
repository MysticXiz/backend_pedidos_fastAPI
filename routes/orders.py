from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_session, verify_token
from schemas.schemas import OrderSchema, OrderItemSchema
from models.models import Order, User, OrderItem
 
orders_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])

def return_orders(orders):
    if orders is None:
        return None
    def _to_dict(o):
        return {
            "id": o.id,
            "user_id": o.user_id,
            "items": getattr(o, "items", []),
            "price": o.price,
            "status": o.status,
        }
    try:
        iter(orders)
    except TypeError:
        return _to_dict(orders)
    return [_to_dict(o) for o in orders if o is not None]

@orders_router.get("/")
async def home():
    return {"message": "Orders Home"}

@orders_router.post("/order")
async def create_order(order_schema: OrderSchema, session: Session = Depends(get_session) , current_user: User = Depends(verify_token)):
    if not current_user.admin and current_user.id != order_schema.user_id:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    new_order = Order(user_id=order_schema.user_id, price=order_schema.price)
    session.add(new_order)
    session.commit()
    return {"message": f"Pedido criado com sucesso. ID do pedido: {new_order.id}"}

@orders_router.get("/order/{order_id}")
async def get_order(order_id: int, session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    order = session.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not current_user.admin and current_user.id != order.user_id:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    print(type(order))
    result = return_orders(order)
    return {"order": result}

@orders_router.post("/order/cancel/{order_id}")
async def cancel_order(order_id: int, session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    order = session.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not current_user.admin and current_user.id != order.user_id:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    order.status = "CANCELADO"
    session.commit()
    return {"message": f"Pedido {order.id} cancelado com sucesso.", "order": order}

@orders_router.post("/order/finish/{order_id}")
async def cancel_order(order_id: int, session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    order = session.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not current_user.admin and current_user.id != order.user_id:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    order.status = "FINALIZADO"
    session.commit()
    return {"message": f"Pedido {order.id} finalizado com sucesso.", "order": order}

@orders_router.post("/order/add-item/{order_id}")
async def add_item_to_order(item_order_schema: OrderItemSchema, order_id: int, session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    order = session.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not current_user.admin and current_user.id != order.user_id:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    new_item = OrderItem(name=item_order_schema.name, price=item_order_schema.price, description=item_order_schema.description, amount=item_order_schema.amount, order_id=order.id)
    session.add(new_item)
    order.calculate_total()
    session.commit()
    return {"message": f"Item adicionado ao pedido {order.id} com sucesso.", "total_price": order.price} 

@orders_router.post("/order/remove-item/{order_item_id}")
async def remove_item_to_order(order_item_id: int, session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    order_item = session.query(OrderItem).filter_by(id=order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    order = session.query(Order).filter_by(id=order_item.order_id).first()
    if not current_user.admin and current_user.id != order.user_id:
        raise HTTPException(status_code=401, detail="Ação não permitida")
    session.delete(order_item)
    order.calculate_total()
    session.commit()
    return {"message": f"Item removido do pedido {order_item.id} com sucesso.","order_price": order.price, "order": order}

@orders_router.get("/list")
async def get_orders(session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    if current_user.admin:
        orders = session.query(Order).all()
    else:
        orders = session.query(Order).filter_by(user_id=current_user.id).limit(10).all()

    result = return_orders(orders)
    return {"orders": result}

@orders_router.get("/list/{user_id}")
async def get_orders(user_id:int, session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    if current_user.admin:
        orders = session.query(Order).filter_by(user_id=user_id).all()
    else:
        orders = session.query(Order).filter_by(user_id=current_user.id).all()
    result = return_orders(orders)
    return {"orders": result}
from pydantic import BaseModel, EmailStr

class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    active: bool | None
    admin: bool | None

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    user_id: int    
    price: float

    class Config:
        from_attributes = True

class OrderItemSchema(BaseModel):
    
    name: str
    amount: int
    description: str | None
    price: float

    class Config:
        from_attributes = True
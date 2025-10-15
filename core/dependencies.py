from models.models import db
from sqlalchemy.orm import sessionmaker
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from models.models import User
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from sqlalchemy.orm import Session

def get_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = session.query(User).filter_by(id=user_id).first()
        return user
    except JWTError as error:
        print(error)
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
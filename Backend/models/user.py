from sqlalchemy import Column, String, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from db import Base

pwd_context_pbkdf2 = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
pwd_context_bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users" 

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False) 
    password_question = Column(String(255), nullable=False)
    password_answer = Column(String(255), nullable=False)
    total_points = Column(Integer, default=0)

    def verify_password(self, plain_password: str) -> bool:
        hashed = self.password or ""
        if hashed.startswith("$2a$") or hashed.startswith("$2b$") or hashed.startswith("$2y$"):
            return pwd_context_bcrypt.verify(plain_password, hashed)
        return pwd_context_pbkdf2.verify(plain_password, hashed)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context_pbkdf2.hash(password)

    def verify_password_and_migrate(self, plain_password: str) -> bool:
        hashed = self.password or ""
        if hashed.startswith("$2a$") or hashed.startswith("$2b$") or hashed.startswith("$2y$"):
            ok = pwd_context_bcrypt.verify(plain_password, hashed)
            if ok:
                self.password = pwd_context_pbkdf2.hash(plain_password)
            return ok
        return pwd_context_pbkdf2.verify(plain_password, hashed)

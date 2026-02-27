from sqlalchemy import Column, String, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from db import Base

# 新密码统一使用 pbkdf2_sha256（环境兼容性更好）。
# 同时保留对历史 bcrypt 哈希的兼容：登录验证时若发现是 bcrypt 格式，则用 bcrypt 校验。
pwd_context_pbkdf2 = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
pwd_context_bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"  # 对应你的用户表名

    # 字段完全匹配你的表结构
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # 存储哈希后的密码
    password_question = Column(String(255), nullable=False)  # 密保问题
    password_answer = Column(String(255), nullable=False)  # 密保答案
    total_points = Column(Integer, default=0)  # 积分（保留）

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

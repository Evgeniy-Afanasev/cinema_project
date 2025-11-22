from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt."""
    return _pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Проверяет соответствие пароля и хеша."""
    return _pwd_context.verify(password, hashed)

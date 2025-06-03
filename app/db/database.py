from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models import Base, UserModel

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    admin = db.query(UserModel).filter_by(email=settings.ADMIN_EMAIL).first()

    if not admin:
        from app.services.auth import (
            get_password_hash,
        )

        admin_user = UserModel(
            id="admin-default",
            full_name=settings.ADMIN_FULL_NAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            role="admin",
        )
        db.add(admin_user)
        db.commit()
        print(f"Default admin created: {settings.ADMIN_EMAIL}")
    else:
        print(f"Admin already exists: {settings.ADMIN_EMAIL}")

    db.close()

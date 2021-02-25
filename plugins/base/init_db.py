from .db_manager import Base, engine


def init_db():
    from .models import vault
    Base.metadata.create_all(bind=engine)


from ..shared.db_manager import Base, engine


def init_db():
    from .models.integration import Integration
    Base.metadata.create_all(bind=engine)


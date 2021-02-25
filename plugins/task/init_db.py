from plugins.base.db_manager import Base, engine


def init_db():
    from .models.results import Results
    from .models.tasks import Task
    Base.metadata.create_all(bind=engine)


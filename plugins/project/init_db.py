from plugins.base.db_manager import Base, engine


def init_db():
    from .models.project import Project
    from .models.quota import ProjectQuota
    from .models.statistics import Statistic

    Base.metadata.create_all(bind=engine)


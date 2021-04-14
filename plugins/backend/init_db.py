from plugins.base.db_manager import Base, engine


def init_db():
    # from .models.api_reports import APIReport
    # from .models.api_tag import APITag
    # from .models.api_baseline import APIBaseline
    from .models.api_tests import ApiTests
    # from .models.api_thresholds import APIThresholds
    Base.metadata.create_all(bind=engine)


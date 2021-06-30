from plugins.base.db_manager import Base, engine


def init_db():
    from .models.api_tests import SecurityTestsDAST
    from .models.security_results import SecurityResultsDAST
    from .models.security_thresholds import SecurityThresholds
    from .models.security_details import SecurityDetails
    from .models.security_reports import SecurityReport
    Base.metadata.create_all(bind=engine)


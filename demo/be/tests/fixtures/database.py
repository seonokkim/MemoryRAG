import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.database import Base, reset_engine
from tests.factories.seed import SeedContext, seed_minimal_dataset


@pytest.fixture()
def db_session() -> Session:
    reset_engine()
    get_settings.cache_clear()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = factory()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    reset_engine()


@pytest.fixture()
def seed(db_session: Session) -> SeedContext:
    return seed_minimal_dataset(db_session)


@pytest.fixture()
def user_id(seed: SeedContext) -> int:
    return seed.user_id


@pytest.fixture()
def swing_session_id(seed: SeedContext) -> int:
    return seed.swing_session_id


@pytest.fixture()
def conversation_id(seed: SeedContext) -> int:
    return seed.conversation_id

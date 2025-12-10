from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from promethium.core.config import get_settings
# Import Base to ensure it's available for users of this module, though technically 
# they should import from api.models.base.
# We import all models here to ensure they are registered with Base.metadata before create_all is called.
from promethium.api.models.base import Base
import promethium.api.models # This triggers registration of all models via __init__.py

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

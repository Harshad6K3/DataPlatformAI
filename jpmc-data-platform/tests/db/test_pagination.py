from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base, PaginatedResult, TestDatabase, paginate


class FakeDataset(Base):
    __tablename__ = "fake_datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


async def create_database() -> TestDatabase:
    database = TestDatabase()
    await database.create_all()
    return database


async def insert_datasets(session) -> None:
    session.add_all([FakeDataset(name=f"dataset-{index}") for index in range(25)])
    await session.commit()


async def test_page_one_returns_twenty_items_and_total() -> None:
    database = await create_database()
    try:
        async with database.get_test_session() as session:
            await insert_datasets(session)
            result = await paginate(session, select(FakeDataset).order_by(FakeDataset.id))

        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 20
        assert result.total == 25
        assert result.pages == 2
    finally:
        await database.dispose()


async def test_page_two_returns_five_items() -> None:
    database = await create_database()
    try:
        async with database.get_test_session() as session:
            await insert_datasets(session)
            result = await paginate(
                session,
                select(FakeDataset).order_by(FakeDataset.id),
                page=2,
            )

        assert len(result.items) == 5
        assert result.page == 2
    finally:
        await database.dispose()
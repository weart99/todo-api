from enum import Enum
from sqlalchemy import String, DateTime, Integer, Enum as SQLAlchemyEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone


class TaskStatus(str, Enum):
    TODO = "To do"
    DOING = "Doing"
    DONE = "Done"
    CANCELLED = "Cancelled"


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    status: Mapped[TaskStatus] = mapped_column(
        SQLAlchemyEnum(TaskStatus), default=TaskStatus.TODO
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # def __init__(
    #     self, title: str, description: str, status: TaskStatus = TaskStatus.TODO
    # ):
    #     self.title = title
    #     self.description = description
    #     self.status = status
    #     self.created_at = datetime.now(timezone.utc)
    #     self.updated_at = datetime.now(timezone.utc)

    # def update_status(self, new_status: TaskStatus):
    #     self.status = new_status
    #     self.updated_at = datetime.now(timezone.utc)

import datetime
# import utcnow as utcnow
from sqlmodel import Field, Session, SQLModel, create_engine, select, TIMESTAMP

def Estimation(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    title: str = Field(default=None, nullable=False)
    max_value: int = Field(default=None, nullable=False)
    min_value: int = Field(default=None, nullable=False)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models.db_model import Role, User

app = typer.Typer()


@app.command(name='create_superuser')
def create_superuser(login: str, password: str):
    super_role = Role(name='superuser', description='superuser')
    dsn = f'postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
    engine = create_engine(dsn, echo=settings.db_echo)
    session = sessionmaker(bind=engine, expire_on_commit=False)

    with session() as session:
        user_db = User(login=login, password=password)
        session.add(super_role)
        session.add(user_db)
        user_db.roles.append(super_role)
        session.commit()

    print('superuser created')


if __name__ == "__main__":
    app()

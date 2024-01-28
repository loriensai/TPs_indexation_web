from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker

def setup_database():

    DATABASE_URL = "postgresql://admin:password@localhost:5433/admin_db"
    engine = create_engine(DATABASE_URL)

    metadata = MetaData()

    webpages = Table(
        'webpages',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('lien', String, nullable=False),
        Column('age', Integer, nullable=False),
        Column('derniere_visite', DateTime, server_default=func.current_timestamp(), nullable=False)
    )

    metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session() 
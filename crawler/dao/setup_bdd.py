from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker


def setup_database():
    """ Configurer la base de données 

    Returns:
        Session : Une instance de session SQLAlchemy pour interagir avec la base de données
    """
    # URL de la base de données PostgreSQL
    DATABASE_URL = "postgresql://admin:password@localhost:5433/admin_db"

    # Créer un moteur SQLAlchemy pour la connexion à la base de données
    engine = create_engine(DATABASE_URL)

    # Créer un objet de métadonnées SQLAlchemy
    metadata = MetaData()

    # Définir la structure de la table 'webpages'
    webpages = Table(
        'webpages',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('lien', String, nullable=False),
        Column('age', Integer, nullable=False),
        Column('derniere_visite', DateTime, server_default=func.current_timestamp(), nullable=False)
    )

    # Créer la table dans la base de données
    metadata.create_all(engine)

    # Créer une session SQLAlchemy pour interagir avec la base de données
    Session = sessionmaker(bind=engine)
    return Session() 
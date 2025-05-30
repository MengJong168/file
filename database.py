from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Database setup
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    licenses = relationship("License", backref="user", cascade="all, delete-orphan")

class License(Base):
    __tablename__ = 'licenses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False)
    volume_serial = Column(String, nullable=False)
    issued_date = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

def init_db():
    engine = create_engine('sqlite:///admin_panel.db')

    # Handle schema migration
    inspector = inspect(engine)
    if 'licenses' in inspector.get_table_names():
        if 'volume_serial' not in [column['name'] for column in inspector.get_columns('licenses')]:
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE licenses ADD COLUMN volume_serial VARCHAR'))
            print("Added volume_serial column to existing licenses table")

    Base.metadata.create_all(engine)
    return engine

# Initialize engine and session factory
engine = init_db()
SessionLocal = sessionmaker(bind=engine)

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

try:
    engine = create_engine('mysql+pymysql://root:Justine%402227@localhost/finance_pulse?charset=utf8mb4', 
                         pool_recycle=3600,
                         pool_pre_ping=True,
                         echo=False)  # Set echo to False to reduce console output
except Exception as e:
    print(f"Database connection error: {e}")
    raise

Base = declarative_base()
Session = sessionmaker(bind=engine)

class Watchlist(Base):
    __tablename__ = 'watchlists'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    added_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(255))
    is_favorite = Column(Boolean, default=False)

class SearchHistory(Base):
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    search_date = Column(DateTime, default=datetime.utcnow)
    period = Column(String(10))

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session"""
    return Session()

def add_to_watchlist(symbol: str, notes: str = None):
    """Add a stock to the watchlist"""
    session = get_session()
    watchlist_item = Watchlist(symbol=symbol, notes=notes)
    session.add(watchlist_item)
    session.commit()
    session.close()

def remove_from_watchlist(symbol: str):
    """Remove a stock from the watchlist"""
    session = get_session()
    session.query(Watchlist).filter(Watchlist.symbol == symbol).delete()
    session.commit()
    session.close()

def get_watchlist():
    """Get all stocks in the watchlist"""
    session = get_session()
    watchlist = session.query(Watchlist).all()
    session.close()
    return watchlist

def add_search_history(symbol: str, period: str):
    """Add a search to history"""
    session = get_session()
    search = SearchHistory(symbol=symbol, period=period)
    session.add(search)
    session.commit()
    session.close()

def get_recent_searches(limit: int = 5):
    """Get recent search history"""
    session = get_session()
    searches = session.query(SearchHistory)\
        .order_by(SearchHistory.search_date.desc())\
        .limit(limit)\
        .all()
    session.close()
    return searches

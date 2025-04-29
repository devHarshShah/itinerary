from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Table, Time, Enum, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
import enum
from datetime import datetime, time
from typing import List, Optional
from sqlalchemy.sql import func

from src.database import Base

# Enums
class TransportType(enum.Enum):
    FLIGHT = "flight"
    FERRY = "ferry" 
    BUS = "bus"
    PRIVATE_CAR = "private_car"
    SHARED_VAN = "shared_van"
    TAXI = "taxi"

class AccommodationType(enum.Enum):
    HOTEL = "hotel"
    RESORT = "resort"
    VILLA = "villa"
    GUESTHOUSE = "guesthouse"
    HOSTEL = "hostel"

class ActivityCategory(enum.Enum):
    NATURE = "nature"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    RELAXATION = "relaxation"
    FOOD_DRINK = "food_drink"
    ENTERTAINMENT = "entertainment"
    SIGHTSEEING = "sightseeing"
    WATER_ACTIVITY = "water_activity"

# Association tables
itinerary_accommodation = Table(
    'itinerary_accommodation', 
    Base.metadata,
    Column('itinerary_day_id', Integer, ForeignKey('itinerary_days.id', ondelete='CASCADE'), primary_key=True),
    Column('accommodation_id', Integer, ForeignKey('accommodations.id'), primary_key=True),
)

itinerary_activity = Table(
    'itinerary_activity', 
    Base.metadata,
    Column('itinerary_day_id', Integer, ForeignKey('itinerary_days.id', ondelete='CASCADE'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('start_time', Time, nullable=True),
    Column('end_time', Time, nullable=True),
    Column('order', Integer, nullable=False),
)

itinerary_transfer = Table(
    'itinerary_transfer', 
    Base.metadata,
    Column('itinerary_day_id', Integer, ForeignKey('itinerary_days.id', ondelete='CASCADE'), primary_key=True),
    Column('transfer_id', Integer, ForeignKey('transfers.id'), primary_key=True),
    Column('order', Integer, nullable=False),
)

# Core Models
class Destination(Base):
    """Geographic locations available in the system"""
    __tablename__ = 'destinations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)  # e.g., "Phuket", "Krabi"
    country = Column(String(100), nullable=False, default="Thailand")
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(255), nullable=True)
    
    # Relationships
    accommodations = relationship("Accommodation", back_populates="destination")
    activities = relationship("Activity", back_populates="destination")
    
    # Transfer relationships as origin or destination
    transfers_from = relationship("Transfer", foreign_keys="Transfer.origin_id", back_populates="origin")
    transfers_to = relationship("Transfer", foreign_keys="Transfer.destination_id", back_populates="destination")
    
    __table_args__ = (
        UniqueConstraint('name', 'region', name='uq_destination_name_region'),
        Index('idx_destination_region', 'region'),
    )
    
    def __repr__(self):
        return f"<Destination(id={self.id}, name='{self.name}', region='{self.region}')>"

class Accommodation(Base):
    """Hotels, resorts, and other places to stay"""
    __tablename__ = 'accommodations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    type = Column(Enum(AccommodationType), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=True)
    stars = Column(Float, nullable=True)
    price_category = Column(Integer, nullable=False)  # 1-5, 1 being budget, 5 being luxury
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    amenities = Column(JSONB, nullable=True)
    image_url = Column(String(255), nullable=True)
    
    # Relationships
    destination = relationship("Destination", back_populates="accommodations")
    
    __table_args__ = (
        UniqueConstraint('name', 'destination_id', name='uq_accommodation_name_destination'),
        Index('idx_accommodation_destination', 'destination_id'),
        Index('idx_accommodation_type', 'type'),
        Index('idx_accommodation_price', 'price_category'),
        CheckConstraint('stars >= 0 AND stars <= 5', name='check_valid_stars'),
        CheckConstraint('price_category >= 1 AND price_category <= 5', name='check_valid_price_category'),
    )
    
    def __repr__(self):
        return f"<Accommodation(id={self.id}, name='{self.name}', type='{self.type}')>"

class Activity(Base):
    """Tours, excursions, and activities"""
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    category = Column(Enum(ActivityCategory), nullable=False)
    description = Column(Text, nullable=True)
    duration_hours = Column(Float, nullable=False)  # Typical duration in hours
    price_range = Column(String(50), nullable=True)  # e.g., "$", "$$", "$$$"
    is_must_see = Column(Boolean, default=False)
    location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(255), nullable=True)
    
    # Relationships
    destination = relationship("Destination", back_populates="activities")
    
    __table_args__ = (
        Index('idx_activity_destination', 'destination_id'),
        Index('idx_activity_category', 'category'),
        Index('idx_activity_must_see', 'is_must_see'),
    )
    
    def __repr__(self):
        return f"<Activity(id={self.id}, name='{self.name}', category='{self.category}')>"

class Transfer(Base):
    """Transportation between destinations"""
    __tablename__ = 'transfers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    origin_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    type = Column(Enum(TransportType), nullable=False)
    duration_hours = Column(Float, nullable=False)  # Typical duration in hours
    description = Column(Text, nullable=True)
    price_range = Column(String(50), nullable=True)  # e.g., "$", "$$", "$$$"
    
    # Relationships
    origin = relationship("Destination", foreign_keys=[origin_id], back_populates="transfers_from")
    destination = relationship("Destination", foreign_keys=[destination_id], back_populates="transfers_to")
    
    __table_args__ = (
        Index('idx_transfer_origin', 'origin_id'),
        Index('idx_transfer_destination', 'destination_id'),
        Index('idx_transfer_type', 'type'),
        CheckConstraint('origin_id != destination_id', name='check_different_locations'),
    )
    
    def __repr__(self):
        return f"<Transfer(id={self.id}, name='{self.name}', type='{self.type}')>"

# Itinerary Models
class Itinerary(Base):
    """Complete trip itinerary"""
    __tablename__ = 'itineraries'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    duration_nights = Column(Integer, nullable=False)
    is_recommended = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    preferences = Column(JSONB, nullable=True)  # Store user preferences if any
    total_estimated_cost = Column(Float, nullable=True)
    
    # Relationships
    days = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan", order_by="ItineraryDay.day_number")
    
    __table_args__ = (
        Index('idx_itinerary_recommended', 'is_recommended'),
        Index('idx_itinerary_duration', 'duration_nights'),
        CheckConstraint('duration_nights > 0', name='check_valid_duration'),
    )
    
    def __repr__(self):
        return f"<Itinerary(id={self.id}, title='{self.title}', duration={self.duration_nights} nights)>"

class ItineraryDay(Base):
    """Single day of an itinerary"""
    __tablename__ = 'itinerary_days'
    
    id = Column(Integer, primary_key=True)
    itinerary_id = Column(Integer, ForeignKey('itineraries.id', ondelete='CASCADE'), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1, 2, 3...
    main_destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    itinerary = relationship("Itinerary", back_populates="days")
    main_destination = relationship("Destination")
    
    # Many-to-many relationships
    accommodations = relationship("Accommodation", secondary=itinerary_accommodation)
    activities = relationship("Activity", secondary=itinerary_activity, order_by="itinerary_activity.c.order")
    transfers = relationship("Transfer", secondary=itinerary_transfer, order_by="itinerary_transfer.c.order")
    
    __table_args__ = (
        UniqueConstraint('itinerary_id', 'day_number', name='uq_itinerary_day_number'),
        Index('idx_itinerary_day_itinerary', 'itinerary_id'),
    )
    
    def __repr__(self):
        return f"<ItineraryDay(id={self.id}, itinerary_id={self.itinerary_id}, day_number={self.day_number})>"
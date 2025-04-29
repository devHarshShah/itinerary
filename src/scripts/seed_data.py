#!/usr/bin/env python3
"""
Data seeder script for Thailand Itinerary App.
Populates the database with realistic data for Phuket and Krabi regions in Thailand.
"""
import os
import sys
import random
from datetime import datetime, time, timedelta
from random import choice, randint, sample, uniform
from pathlib import Path

# Add the src directory to the Python path to ensure imports work correctly
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
root_dir = src_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import required modules with proper src prefixes
from sqlalchemy import text, inspect, func

# Use environment variable to determine import style
if os.environ.get("INSIDE_DOCKER", "false").lower() == "true":
    # Docker environment - use absolute imports
    from src.database import SessionLocal, engine
    from src.models import (
        Destination, Accommodation, Activity, Transfer, Itinerary, ItineraryDay,
        AccommodationType, ActivityCategory, TransportType, Base
    )
    from src.auth.models import User, UserRole
    from src.auth.service import get_password_hash
else:
    # Local environment - use relative imports if possible
    try:
        from src.database import SessionLocal, engine
        from src.models import (
            Destination, Accommodation, Activity, Transfer, Itinerary, ItineraryDay,
            AccommodationType, ActivityCategory, TransportType, Base
        )
        from src.auth.models import User, UserRole
        from src.auth.service import get_password_hash
    except ImportError:
        # If that fails, try relative imports from current location
        from database import SessionLocal, engine
        from models import (
            Destination, Accommodation, Activity, Transfer, Itinerary, ItineraryDay,
            AccommodationType, ActivityCategory, TransportType, Base
        )
        from auth.models import User, UserRole
        from auth.service import get_password_hash

# Create a database session
db = SessionLocal()

# ---------------------- Helper Functions ----------------------

def create_tables():
    """Create all tables in the database if they don't exist."""
    print("Checking and creating database tables...")
    inspector = inspect(engine)
    
    # Check if the destinations table exists
    if not inspector.has_table("destinations"):
        print("Tables don't exist. Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    else:
        print("Tables already exist. Skipping creation.")

def clear_tables():
    """Clear all data from tables in the correct order to avoid constraint violations."""
    print("Clearing existing data...")
    # Clear junction tables and dependent tables first
    db.execute(text("DELETE FROM itinerary_transfer"))
    db.execute(text("DELETE FROM itinerary_activity"))
    db.execute(text("DELETE FROM itinerary_accommodation"))
    db.execute(text("DELETE FROM itinerary_days"))
    db.execute(text("DELETE FROM itineraries"))
    db.execute(text("DELETE FROM transfers"))
    db.execute(text("DELETE FROM activities"))
    db.execute(text("DELETE FROM accommodations"))
    db.execute(text("DELETE FROM destinations"))
    db.execute(text("DELETE FROM users"))
    db.commit()
    print("All tables cleared.")

def create_users():
    """Create admin and regular user accounts."""
    print("Creating users...")
    
    # Create admin user
    admin_user = User(
        email="admin@travelthailand.com",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("Admin123!"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin_user)
    
    # Create regular user
    regular_user = User(
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        hashed_password=get_password_hash("Thailand2025!"),
        role=UserRole.USER,
        is_active=True
    )
    db.add(regular_user)
    
    db.commit()
    print("Created admin and regular user accounts.")
    return admin_user, regular_user

def create_destinations():
    """Create destination entries for Phuket and Krabi regions."""
    print("Creating destinations...")
    
    destinations = [
        # Phuket destinations
        Destination(
            name="Patong Beach",
            region="Phuket",
            country="Thailand",
            description="Patong is Phuket's most famous beach resort and is always busy with visitors. This wide, sandy beach is lined with hotels, restaurants, and vendors.",
            latitude=7.9016,
            longitude=98.2987,
            image_url="https://example.com/images/patong-beach.jpg"
        ),
        Destination(
            name="Kata Beach",
            region="Phuket",
            country="Thailand",
            description="A more relaxed beach destination with beautiful white sand and clear water, popular for swimming and snorkeling.",
            latitude=7.8206,
            longitude=98.2987,
            image_url="https://example.com/images/kata-beach.jpg"
        ),
        Destination(
            name="Phuket Old Town",
            region="Phuket",
            country="Thailand",
            description="The historical center of Phuket with charming Sino-Portuguese architecture, colorful buildings, and vibrant street art.",
            latitude=7.8853,
            longitude=98.3876,
            image_url="https://example.com/images/phuket-old-town.jpg"
        ),
        Destination(
            name="Karon Beach",
            region="Phuket",
            country="Thailand",
            description="One of the longest beaches in Phuket with fine white sand and excellent swimming conditions during the high season.",
            latitude=7.8425,
            longitude=98.2940,
            image_url="https://example.com/images/karon-beach.jpg"
        ),
        
        # Krabi destinations
        Destination(
            name="Ao Nang",
            region="Krabi",
            country="Thailand",
            description="The main tourist hub of Krabi, with a beautiful beach lined with restaurants, shops, and accommodation options.",
            latitude=8.0317,
            longitude=98.8220,
            image_url="https://example.com/images/ao-nang.jpg"
        ),
        Destination(
            name="Railay Beach",
            region="Krabi",
            country="Thailand",
            description="A stunning peninsula accessible only by boat, famous for its dramatic limestone cliffs, clear waters, and rock climbing opportunities.",
            latitude=8.0119,
            longitude=98.8372,
            image_url="https://example.com/images/railay-beach.jpg"
        ),
        Destination(
            name="Koh Phi Phi",
            region="Krabi",
            country="Thailand",
            description="An archipelago of six islands with stunning beaches, coral reefs, and the famous Maya Bay, featured in the movie 'The Beach'.",
            latitude=7.7407,
            longitude=98.7784,
            image_url="https://example.com/images/phi-phi-islands.jpg"
        ),
        Destination(
            name="Krabi Town",
            region="Krabi",
            country="Thailand",
            description="The provincial capital with riverside views, markets, and a relaxed atmosphere, serving as a gateway to Krabi's coastal attractions.",
            latitude=8.0862,
            longitude=98.9062,
            image_url="https://example.com/images/krabi-town.jpg"
        ),
    ]
    
    for destination in destinations:
        db.add(destination)
    
    db.commit()
    print(f"Created {len(destinations)} destinations.")
    return destinations

def create_accommodations(destinations):
    """Create accommodation entries for each destination."""
    print("Creating accommodations...")
    
    accommodations = []
    
    # Patong Beach accommodations
    patong = db.query(Destination).filter_by(name="Patong Beach").first()
    accommodations.extend([
        Accommodation(
            name="Patong Bay Luxury Resort",
            destination_id=patong.id,
            type=AccommodationType.RESORT,
            description="Luxurious beachfront resort with panoramic ocean views, multiple swimming pools, and world-class dining.",
            address="123 Beach Road, Patong, Phuket",
            stars=5.0,
            price_category=5,
            latitude=7.9040,
            longitude=98.2965,
            amenities={"wifi": True, "pool": True, "spa": True, "gym": True, "restaurant": True, "beach_access": True},
            image_url="https://example.com/images/patong-bay-resort.jpg"
        ),
        Accommodation(
            name="Sunset Beach Hotel",
            destination_id=patong.id,
            type=AccommodationType.HOTEL,
            description="Mid-range hotel just a short walk from the beach with comfortable rooms and a rooftop pool.",
            address="456 Sunset Street, Patong, Phuket",
            stars=3.5,
            price_category=3,
            latitude=7.9030,
            longitude=98.2980,
            amenities={"wifi": True, "pool": True, "restaurant": True},
            image_url="https://example.com/images/sunset-beach-hotel.jpg"
        ),
        Accommodation(
            name="Backpacker's Haven",
            destination_id=patong.id,
            type=AccommodationType.HOSTEL,
            description="Affordable hostel with dormitory and private rooms, popular with young travelers and backpackers.",
            address="789 Party Road, Patong, Phuket",
            stars=2.5,
            price_category=1,
            latitude=7.9010,
            longitude=98.3010,
            amenities={"wifi": True, "shared_kitchen": True, "common_area": True},
            image_url="https://example.com/images/backpackers-haven.jpg"
        ),
    ])
    
    # Add more accommodations for each destination
    # Kata Beach
    kata = db.query(Destination).filter_by(name="Kata Beach").first()
    accommodations.extend([
        Accommodation(
            name="Kata Beachfront Resort & Spa",
            destination_id=kata.id,
            type=AccommodationType.RESORT,
            description="Elegant beachfront resort with traditional Thai architecture and modern amenities.",
            address="101 Kata Beach Road, Phuket",
            stars=4.5,
            price_category=4,
            latitude=7.8210,
            longitude=98.2965,
            amenities={"wifi": True, "pool": True, "spa": True, "restaurant": True, "beach_access": True},
            image_url="https://example.com/images/kata-resort.jpg"
        ),
        Accommodation(
            name="Kata Garden Villa",
            destination_id=kata.id,
            type=AccommodationType.VILLA,
            description="Private villa with garden views, a short walk from the beach.",
            address="202 Garden Lane, Kata, Phuket",
            stars=4.0,
            price_category=4,
            latitude=7.8200,
            longitude=98.2980,
            amenities={"wifi": True, "private_pool": True, "kitchen": True},
            image_url="https://example.com/images/kata-villa.jpg"
        ),
    ])
    
    # Railay Beach
    railay = db.query(Destination).filter_by(name="Railay Beach").first()
    accommodations.extend([
        Accommodation(
            name="Railay Bay Resort & Spa",
            destination_id=railay.id,
            type=AccommodationType.RESORT,
            description="Luxurious resort located directly on the stunning Railay Beach with limestone cliff views.",
            address="1 Railay Beach East, Krabi",
            stars=4.5,
            price_category=5,
            latitude=8.0125,
            longitude=98.8375,
            amenities={"wifi": True, "pool": True, "spa": True, "restaurant": True, "beach_access": True},
            image_url="https://example.com/images/railay-resort.jpg"
        ),
        Accommodation(
            name="Climbing Home Guesthouse",
            destination_id=railay.id,
            type=AccommodationType.GUESTHOUSE,
            description="Simple but comfortable accommodation popular with rock climbers and budget travelers.",
            address="345 Railay East, Krabi",
            stars=3.0,
            price_category=2,
            latitude=8.0130,
            longitude=98.8390,
            amenities={"wifi": True, "climbing_gear_rental": True},
            image_url="https://example.com/images/climbing-home.jpg"
        ),
    ])
    
    # Add accommodations for the remaining destinations
    for destination in destinations:
        if destination.name not in ["Patong Beach", "Kata Beach", "Railay Beach"]:
            # Create 2-3 accommodations for each remaining destination
            for i in range(randint(2, 3)):
                price_cat = randint(1, 5)
                stars = round(uniform(2.0, 5.0), 1) if price_cat > 1 else round(uniform(1.0, 3.0), 1)
                acc_type = choice(list(AccommodationType))
                
                accommodations.append(
                    Accommodation(
                        name=f"{destination.name} {acc_type.value.title()} {i+1}",
                        destination_id=destination.id,
                        type=acc_type,
                        description=f"A {'luxurious' if price_cat > 3 else 'comfortable' if price_cat > 1 else 'budget-friendly'} {acc_type.value} in {destination.name}.",
                        address=f"{100+i} Main Street, {destination.name}, {destination.region}",
                        stars=stars,
                        price_category=price_cat,
                        latitude=destination.latitude + uniform(-0.01, 0.01),
                        longitude=destination.longitude + uniform(-0.01, 0.01),
                        amenities={"wifi": True, "pool": price_cat > 2, "restaurant": price_cat > 1},
                        image_url=f"https://example.com/images/{destination.name.lower().replace(' ', '-')}-acc-{i+1}.jpg"
                    )
                )
    
    for accommodation in accommodations:
        db.add(accommodation)
    
    db.commit()
    print(f"Created {len(accommodations)} accommodations.")
    return accommodations

def create_activities(destinations):
    """Create activity entries for each destination."""
    print("Creating activities...")
    
    activities = []
    
    # Patong Beach activities
    patong = db.query(Destination).filter_by(name="Patong Beach").first()
    activities.extend([
        Activity(
            name="Patong Beach Day",
            destination_id=patong.id,
            category=ActivityCategory.RELAXATION,
            description="Enjoy a day relaxing on the famous Patong Beach with sun loungers, umbrellas, and refreshments.",
            duration_hours=6.0,
            price_range="$",
            is_must_see=True,
            location="Patong Beach",
            latitude=patong.latitude,
            longitude=patong.longitude,
            image_url="https://example.com/images/patong-beach-activity.jpg"
        ),
        Activity(
            name="Bangla Road Night Tour",
            destination_id=patong.id,
            category=ActivityCategory.ENTERTAINMENT,
            description="Experience the vibrant nightlife of Phuket's famous Bangla Road with bars, clubs, and street performances.",
            duration_hours=4.0,
            price_range="$$",
            is_must_see=True,
            location="Bangla Road, Patong",
            latitude=7.8933,
            longitude=98.2967,
            image_url="https://example.com/images/bangla-road.jpg"
        ),
        Activity(
            name="Thai Cooking Class",
            destination_id=patong.id,
            category=ActivityCategory.FOOD_DRINK,
            description="Learn to cook authentic Thai dishes with local ingredients at a popular cooking school.",
            duration_hours=3.0,
            price_range="$$",
            is_must_see=False,
            location="Patong Cooking School",
            latitude=7.9022,
            longitude=98.3032,
            image_url="https://example.com/images/thai-cooking.jpg"
        ),
    ])
    
    # Phi Phi Islands activities
    phi_phi = db.query(Destination).filter_by(name="Koh Phi Phi").first()
    activities.extend([
        Activity(
            name="Maya Bay Snorkeling Tour",
            destination_id=phi_phi.id,
            category=ActivityCategory.WATER_ACTIVITY,
            description="Visit the famous Maya Bay (where 'The Beach' was filmed) and snorkel in crystal clear waters with colorful marine life.",
            duration_hours=7.0,
            price_range="$$$",
            is_must_see=True,
            location="Maya Bay, Phi Phi Islands",
            latitude=7.6780,
            longitude=98.7673,
            image_url="https://example.com/images/maya-bay.jpg"
        ),
        Activity(
            name="Phi Phi Viewpoint Hike",
            destination_id=phi_phi.id,
            category=ActivityCategory.ADVENTURE,
            description="Hike to the famous Phi Phi viewpoint for panoramic views of the island's twin bays.",
            duration_hours=2.0,
            price_range="$",
            is_must_see=True,
            location="Phi Phi Viewpoint",
            latitude=7.7407,
            longitude=98.7784,
            image_url="https://example.com/images/phi-phi-viewpoint.jpg"
        ),
    ])
    
    # Railay Beach activities
    railay = db.query(Destination).filter_by(name="Railay Beach").first()
    activities.extend([
        Activity(
            name="Rock Climbing Adventure",
            destination_id=railay.id,
            category=ActivityCategory.ADVENTURE,
            description="Try rock climbing on Railay's world-famous limestone cliffs with professional instructors.",
            duration_hours=4.0,
            price_range="$$",
            is_must_see=True,
            location="Railay East Cliffs",
            latitude=8.0119,
            longitude=98.8390,
            image_url="https://example.com/images/railay-climbing.jpg"
        ),
        Activity(
            name="Four Islands Boat Tour",
            destination_id=railay.id,
            category=ActivityCategory.WATER_ACTIVITY,
            description="Explore four stunning islands around Railay by longtail boat, with snorkeling and beach time.",
            duration_hours=6.0,
            price_range="$$",
            is_must_see=True,
            location="Railay Beach",
            latitude=8.0119,
            longitude=98.8372,
            image_url="https://example.com/images/four-islands-tour.jpg"
        ),
        Activity(
            name="Phra Nang Cave Beach Visit",
            destination_id=railay.id,
            category=ActivityCategory.RELAXATION,
            description="Visit the stunning Phra Nang Cave Beach with its unique princess cave shrine and beautiful scenery.",
            duration_hours=3.0,
            price_range="$",
            is_must_see=True,
            location="Phra Nang Cave Beach",
            latitude=8.0082,
            longitude=98.8398,
            image_url="https://example.com/images/phra-nang-beach.jpg"
        ),
    ])
    
    # Add activities for the remaining destinations
    for destination in destinations:
        if destination.name not in ["Patong Beach", "Koh Phi Phi", "Railay Beach"]:
            # Create 3-5 activities for each remaining destination
            categories = list(ActivityCategory)
            for i in range(randint(3, 5)):
                category = choice(categories)
                duration = round(uniform(1.0, 8.0), 1)
                price_range = choice(["$", "$$", "$$$"])
                is_must_see = random.random() > 0.7  # 30% chance of being must-see
                
                activities.append(
                    Activity(
                        name=f"{destination.name} {category.value.replace('_', ' ').title()} {i+1}",
                        destination_id=destination.id,
                        category=category,
                        description=f"A popular {category.value.replace('_', ' ')} activity in {destination.name}.",
                        duration_hours=duration,
                        price_range=price_range,
                        is_must_see=is_must_see,
                        location=f"{destination.name}, {destination.region}",
                        latitude=destination.latitude + uniform(-0.01, 0.01),
                        longitude=destination.longitude + uniform(-0.01, 0.01),
                        image_url=f"https://example.com/images/{destination.name.lower().replace(' ', '-')}-act-{i+1}.jpg"
                    )
                )
    
    for activity in activities:
        db.add(activity)
    
    db.commit()
    print(f"Created {len(activities)} activities.")
    return activities

def create_transfers(destinations):
    """Create transfer options between destinations."""
    print("Creating transfers...")
    
    transfers = []
    
    # Dictionary to map regions to their destinations
    regions = {}
    for destination in destinations:
        if destination.region not in regions:
            regions[destination.region] = []
        regions[destination.region].append(destination)
    
    # Define transport types appropriate for different distance ranges
    short_distance_options = [TransportType.TAXI, TransportType.PRIVATE_CAR, TransportType.SHARED_VAN]
    medium_distance_options = [TransportType.BUS, TransportType.SHARED_VAN, TransportType.PRIVATE_CAR]
    long_distance_options = [TransportType.FERRY, TransportType.FLIGHT]
    
    # Create transfers within each region
    for region_name, region_destinations in regions.items():
        for i, origin in enumerate(region_destinations):
            for destination in region_destinations[i+1:]:
                # Calculate approximate distance (this is simplified)
                lat_diff = abs(origin.latitude - destination.latitude)
                lon_diff = abs(origin.longitude - destination.longitude)
                approx_distance = (lat_diff**2 + lon_diff**2)**0.5 * 111  # Rough km conversion
                
                # Skip if places are very close
                if approx_distance < 0.05:
                    continue
                
                # Determine appropriate transport types based on distance
                if approx_distance < 15:  # Short distance within region
                    transport_options = short_distance_options
                    duration_factor = 1.0  # Hours per 10km
                    price_range = "$"
                else:  # Medium distance within region
                    transport_options = medium_distance_options
                    duration_factor = 0.8  # Hours per 10km
                    price_range = "$$"
                
                # Create transfers between these destinations in both directions
                for transport_type in sample(transport_options, min(2, len(transport_options))):
                    duration = round(approx_distance * duration_factor / 10, 1)
                    if duration < 0.5:
                        duration = 0.5  # Minimum 30 minutes
                    
                    # Origin to destination
                    transfers.append(
                        Transfer(
                            name=f"{transport_type.value.replace('_', ' ').title()} from {origin.name} to {destination.name}",
                            origin_id=origin.id,
                            destination_id=destination.id,
                            type=transport_type,
                            duration_hours=duration,
                            description=f"Regular {transport_type.value.replace('_', ' ')} service connecting {origin.name} to {destination.name}.",
                            price_range=price_range
                        )
                    )
                    
                    # Destination to origin (symmetric)
                    transfers.append(
                        Transfer(
                            name=f"{transport_type.value.replace('_', ' ').title()} from {destination.name} to {origin.name}",
                            origin_id=destination.id,
                            destination_id=origin.id,
                            type=transport_type,
                            duration_hours=duration,
                            description=f"Regular {transport_type.value.replace('_', ' ')} service connecting {destination.name} to {origin.name}.",
                            price_range=price_range
                        )
                    )
    
    # Create transfers between regions
    phuket_destinations = regions.get("Phuket", [])
    krabi_destinations = regions.get("Krabi", [])
    
    for phuket_dest in phuket_destinations:
        for krabi_dest in krabi_destinations:
            # Skip certain combinations that wouldn't have direct connections
            if phuket_dest.name == "Phuket Old Town" and krabi_dest.name not in ["Krabi Town", "Ao Nang"]:
                continue
            
            # Create ferry and flight options between major points
            for transport_type in long_distance_options:
                if transport_type == TransportType.FERRY:
                    duration = round(uniform(2.0, 3.5), 1)
                    price_range = "$$"
                else:  # Flight
                    duration = round(uniform(0.5, 1.0), 1)
                    price_range = "$$$"
                
                # Phuket to Krabi
                transfers.append(
                    Transfer(
                        name=f"{transport_type.value.title()} from {phuket_dest.name} to {krabi_dest.name}",
                        origin_id=phuket_dest.id,
                        destination_id=krabi_dest.id,
                        type=transport_type,
                        duration_hours=duration,
                        description=f"{transport_type.value.title()} service connecting {phuket_dest.name} to {krabi_dest.name}.",
                        price_range=price_range
                    )
                )
                
                # Krabi to Phuket
                transfers.append(
                    Transfer(
                        name=f"{transport_type.value.title()} from {krabi_dest.name} to {phuket_dest.name}",
                        origin_id=krabi_dest.id,
                        destination_id=phuket_dest.id,
                        type=transport_type,
                        duration_hours=duration,
                        description=f"{transport_type.value.title()} service connecting {krabi_dest.name} to {phuket_dest.name}.",
                        price_range=price_range
                    )
                )
    
    for transfer in transfers:
        db.add(transfer)
    
    db.commit()
    print(f"Created {len(transfers)} transfers.")
    return transfers

def create_itineraries(destinations, accommodations, activities, transfers):
    """Create sample itineraries."""
    print("Creating itineraries...")
    
    # Generate a 3-day Phuket Itinerary
    phuket_itinerary = Itinerary(
        title="Phuket Beach Getaway",
        duration_nights=3,
        description="A relaxing 3-day beach vacation in Phuket exploring the island's best beaches and attractions.",
        is_recommended=True,
        preferences={"beach": True, "relaxation": True, "food": True, "nightlife": True},
        total_estimated_cost=12000.00  # Thai Baht
    )
    db.add(phuket_itinerary)
    db.flush()  # To get the ID
    
    # Patong, Kata, and Karon destinations
    patong = db.query(Destination).filter_by(name="Patong Beach").first()
    kata = db.query(Destination).filter_by(name="Kata Beach").first()
    karon = db.query(Destination).filter_by(name="Karon Beach").first()
    
    # Patong accommodations
    patong_accommodations = db.query(Accommodation).filter_by(destination_id=patong.id).all()
    
    # Create Day 1: Patong Beach
    day1 = ItineraryDay(
        itinerary_id=phuket_itinerary.id,
        day_number=1,
        main_destination_id=patong.id,
        description="Arrive in Patong and explore the famous beach and vibrant nightlife."
    )
    db.add(day1)
    db.flush()
    
    # Add accommodation for day 1
    patong_resort = next((acc for acc in patong_accommodations if acc.type == AccommodationType.RESORT), patong_accommodations[0])
    day1.accommodations.append(patong_resort)
    
    # Add activities for day 1
    patong_activities = db.query(Activity).filter_by(destination_id=patong.id).all()
    beach_day = next((act for act in patong_activities if "Beach" in act.name), None)
    nightlife = next((act for act in patong_activities if "Night" in act.name), None)
    
    if beach_day:
        db.execute(
            text('INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order") VALUES (:day_id, :act_id, :start, :end, :order)'),
            {"day_id": day1.id, "act_id": beach_day.id, "start": time(10, 0), "end": time(16, 0), "order": 1}
        )
    
    if nightlife:
        db.execute(
            text('INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order") VALUES (:day_id, :act_id, :start, :end, :order)'),
            {"day_id": day1.id, "act_id": nightlife.id, "start": time(20, 0), "end": time(23, 59), "order": 2}
        )
    
    # Create Day 2: Kata Beach
    day2 = ItineraryDay(
        itinerary_id=phuket_itinerary.id,
        day_number=2,
        main_destination_id=kata.id,
        description="Day trip to the beautiful Kata Beach for a change of scenery."
    )
    db.add(day2)
    db.flush()
    
    # Keep same accommodation (still in Patong)
    day2.accommodations.append(patong_resort)
    
    # Add transfer from Patong to Kata
    patong_to_kata = db.query(Transfer).filter_by(origin_id=patong.id, destination_id=kata.id).first()
    if patong_to_kata:
        db.execute(
            text('INSERT INTO itinerary_transfer (itinerary_day_id, transfer_id, "order") VALUES (:day_id, :transfer_id, :order)'),
            {"day_id": day2.id, "transfer_id": patong_to_kata.id, "order": 1}
        )
    
    # Add Kata Beach activities
    kata_activities = db.query(Activity).filter_by(destination_id=kata.id).all()
    if kata_activities:
        db.execute(
            text('INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order") VALUES (:day_id, :act_id, :start, :end, :order)'),
            {"day_id": day2.id, "act_id": kata_activities[0].id, "start": time(11, 0), "end": time(16, 0), "order": 2}
        )
    
    # Add transfer back to Patong
    kata_to_patong = db.query(Transfer).filter_by(origin_id=kata.id, destination_id=patong.id).first()
    if kata_to_patong:
        db.execute(
            text('INSERT INTO itinerary_transfer (itinerary_day_id, transfer_id, "order") VALUES (:day_id, :transfer_id, :order)'),
            {"day_id": day2.id, "transfer_id": kata_to_patong.id, "order": 3}
        )
    
    # Create Day 3: Phuket Old Town
    old_town = db.query(Destination).filter_by(name="Phuket Old Town").first()
    day3 = ItineraryDay(
        itinerary_id=phuket_itinerary.id,
        day_number=3,
        main_destination_id=old_town.id,
        description="Explore the historical and cultural Phuket Old Town before departure."
    )
    db.add(day3)
    db.flush()
    
    # Keep same accommodation for the last night
    day3.accommodations.append(patong_resort)
    
    # Add transfer to Old Town
    patong_to_old_town = db.query(Transfer).filter_by(origin_id=patong.id, destination_id=old_town.id).first()
    if patong_to_old_town:
        db.execute(
            text('INSERT INTO itinerary_transfer (itinerary_day_id, transfer_id, "order") VALUES (:day_id, :transfer_id, :order)'),
            {"day_id": day3.id, "transfer_id": patong_to_old_town.id, "order": 1}
        )
    
    # Add Old Town activities
    old_town_activities = db.query(Activity).filter_by(destination_id=old_town.id).all()
    if old_town_activities:
        db.execute(
            text('INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order") VALUES (:day_id, :act_id, :start, :end, :order)'),
            {"day_id": day3.id, "act_id": old_town_activities[0].id, "start": time(10, 0), "end": time(15, 0), "order": 2}
        )
    
    # Add transfer back to Patong
    old_town_to_patong = db.query(Transfer).filter_by(origin_id=old_town.id, destination_id=patong.id).first()
    if old_town_to_patong:
        db.execute(
            text('INSERT INTO itinerary_transfer (itinerary_day_id, transfer_id, "order") VALUES (:day_id, :transfer_id, :order)'),
            {"day_id": day3.id, "transfer_id": old_town_to_patong.id, "order": 3}
        )
    
    # Generate a 5-day Phuket-Krabi Combo Itinerary
    combo_itinerary = Itinerary(
        title="Phuket and Krabi Explorer",
        duration_nights=5,
        description="The perfect 5-day tour combining the best of Phuket and Krabi provinces with stunning beaches and landscapes.",
        is_recommended=True,
        preferences={"beach": True, "adventure": True, "nature": True, "island_hopping": True},
        total_estimated_cost=25000.00  # Thai Baht
    )
    db.add(combo_itinerary)
    db.flush()
    
    # Get Krabi destinations
    ao_nang = db.query(Destination).filter_by(name="Ao Nang").first()
    railay = db.query(Destination).filter_by(name="Railay Beach").first()
    phi_phi = db.query(Destination).filter_by(name="Koh Phi Phi").first()
    
    # Create days for combo itinerary (simplified for brevity)
    # Day 1-2: Patong
    combo_day1 = ItineraryDay(
        itinerary_id=combo_itinerary.id,
        day_number=1,
        main_destination_id=patong.id,
        description="Arrive in Phuket and enjoy Patong Beach."
    )
    db.add(combo_day1)
    db.flush()
    combo_day1.accommodations.append(patong_resort)
    
    combo_day2 = ItineraryDay(
        itinerary_id=combo_itinerary.id,
        day_number=2,
        main_destination_id=phi_phi.id,
        description="Day trip to the stunning Phi Phi Islands."
    )
    db.add(combo_day2)
    db.flush()
    combo_day2.accommodations.append(patong_resort)
    
    # Day 3-5: Krabi
    railay_acc = db.query(Accommodation).filter_by(destination_id=railay.id).first()
    
    combo_day3 = ItineraryDay(
        itinerary_id=combo_itinerary.id,
        day_number=3,
        main_destination_id=ao_nang.id,
        description="Travel to Krabi and explore Ao Nang beach area."
    )
    db.add(combo_day3)
    db.flush()
    combo_day3.accommodations.append(railay_acc)
    
    combo_day4 = ItineraryDay(
        itinerary_id=combo_itinerary.id,
        day_number=4,
        main_destination_id=railay.id,
        description="Full day at the stunning Railay Beach."
    )
    db.add(combo_day4)
    db.flush()
    combo_day4.accommodations.append(railay_acc)
    
    combo_day5 = ItineraryDay(
        itinerary_id=combo_itinerary.id,
        day_number=5,
        main_destination_id=railay.id,
        description="Last day to enjoy Railay before departure."
    )
    db.add(combo_day5)
    db.flush()
    combo_day5.accommodations.append(railay_acc)
    
    # Add a basic activity to each day (simplified)
    for day in [combo_day1, combo_day2, combo_day3, combo_day4, combo_day5]:
        dest_activities = db.query(Activity).filter_by(destination_id=day.main_destination_id).all()
        if dest_activities:
            db.execute(
                text('INSERT INTO itinerary_activity (itinerary_day_id, activity_id, start_time, end_time, "order") VALUES (:day_id, :act_id, :start, :end, :order)'),
                {"day_id": day.id, "act_id": dest_activities[0].id, "start": time(10, 0), "end": time(16, 0), "order": 1}
            )
    
    db.commit()
    print(f"Created 2 itineraries with their respective days, accommodations, activities, and transfers.")

# ---------------------- Main Execution ----------------------

def seed_data():
    """Main function to seed all data."""
    try:
        # Create tables if they don't exist
        create_tables()
        
        # Clear existing data if the clear_tables function is uncommented
        # clear_tables()
        
        # Create users
        admin_user, regular_user = create_users()
        
        # Create destinations
        destinations = create_destinations()
        
        # Create accommodations
        accommodations = create_accommodations(destinations)
        
        # Create activities
        activities = create_activities(destinations)
        
        # Create transfers
        transfers = create_transfers(destinations)
        
        # Create itineraries
        create_itineraries(destinations, accommodations, activities, transfers)
        
        print("Data seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error during data seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
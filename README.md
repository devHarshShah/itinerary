# Itinerary API

A comprehensive travel itinerary management system built with FastAPI, SQLAlchemy, and PostgreSQL.

## 📋 Project Overview

This project provides a complete API for managing travel itineraries, including:

- User authentication and authorization
- Destination management
- Accommodation bookings
- Activity planning
- Transportation arrangements
- Complete itinerary creation and management

## 🏗️ Architecture

The application follows a modular architecture with the following components:

- **FastAPI Framework**: High-performance web framework
- **SQLAlchemy ORM**: Database interaction layer
- **Alembic**: Database migration management
- **PostgreSQL**: Primary database (with SQLite support for testing)
- **Docker**: Containerization for development and deployment

## 🔧 Technology Stack

- **Backend**: Python 3.13, FastAPI
- **Database**: PostgreSQL, SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing
- **API Documentation**: Swagger UI (via FastAPI)
- **Testing**: Pytest
- **Containerization**: Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.13 (for local development without Docker)

### Running with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd itinerary
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. The API will be available at [http://localhost:8000](http://localhost:8000)
   - API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Alternative documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Docker Compose will:
- Build the application container
- Start a PostgreSQL database
- Run database migrations automatically
- Seed the database with initial data (if needed)
- Start the FastAPI application

### Running Locally (Development)

1. Install dependencies:
   ```bash
   pip install -r requirements/requirements.txt
   ```

2. Set up the database:
   ```bash
   # Set your database connection environment variables
   export DB_HOST=localhost
   export DB_NAME=itinerary_db
   export DB_USER=postgres
   export DB_PASSWORD=postgres
   
   # Run migrations
   alembic upgrade head
   
   # Seed initial data (if needed)
   python -m src.scripts.seed_data
   ```

3. Start the application:
   ```bash
   uvicorn src.main:app --reload
   ```

## 🧪 Testing

The project includes both unit and integration tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/
```

## 📁 Project Structure

```
├── alembic/              # Database migration files
├── requirements/         # Project dependencies
├── src/                  # Source code
│   ├── accommodation/    # Accommodation module
│   ├── activity/         # Activity module
│   ├── auth/             # Authentication and user management
│   ├── destination/      # Destination module
│   ├── itinerary/        # Itinerary module
│   ├── mcp/              # Model Context Protocol integration
│   ├── scripts/          # Utility scripts
│   ├── transfer/         # Transportation module
│   ├── database.py       # Database connection setup
│   └── main.py           # Application entry point
├── tests/                # Test suite
│   ├── integration/      # Integration tests
│   ├── unit/             # Unit tests
│   └── utils/            # Test utilities
├── Dockerfile            # Container definition
├── docker-compose.yml    # Container orchestration
├── alembic.ini           # Alembic configuration
└── start.sh              # Application startup script
```

## 🔑 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive access token

### Itineraries
- `GET /itineraries` - List all itineraries
- `POST /itineraries` - Create a new itinerary
- `GET /itineraries/{id}` - Get a specific itinerary
- `PUT /itineraries/{id}` - Update an itinerary
- `DELETE /itineraries/{id}` - Delete an itinerary

Additional endpoints are available for managing destinations, accommodations, activities, and transfers.
For full API documentation, visit the [Swagger UI](http://localhost:8000/docs) after starting the application.

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Remove volumes (will delete database data)
docker-compose down -v
```
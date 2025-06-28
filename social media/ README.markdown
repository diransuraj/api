# FastAPI Social Media API

A modern REST API built with FastAPI for a social media/blogging platform.

## Features

- **User Management** - User registration and authentication
- **Post Management** - Create, read, update, and delete posts
- **Authentication** - Secure user authentication system
- **Database Integration** - PostgreSQL with SQLAlchemy ORM

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **psycopg2** - PostgreSQL adapter

## Project Structure

```
├── main.py          # Application entry point
├── models.py        # Database models
├── schemas.py       # Pydantic models
├── utils.py         # Utility functions
├── database.py      # Database configuration
└── routers/
    ├── post.py      # Post-related endpoints
    ├── user.py      # User management endpoints
    └── auth.py      # Authentication endpoints
```

## Setup

1. Install dependencies:
   ```bash
   pip install fastapi psycopg2 sqlalchemy
   ```

2. Configure PostgreSQL database connection in `main.py`

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

- `/` - Root endpoint
- `/posts` - Post management
- `/users` - User management  
- `/auth` - Authentication

The API automatically generates interactive documentation at `/docs` when running.

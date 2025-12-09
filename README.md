# EduNova Backend

Django REST Framework backend for EduNova application with JWT authentication and PostgreSQL.

## Features

- Django 5.0 with Django REST Framework
- JWT authentication using `djangorestframework-simplejwt`
- PostgreSQL database
- CORS enabled for React frontend
- User registration and authentication
- User profiles with full_name field

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=edunova_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Set Up PostgreSQL Database

**Option A: Using psql (Recommended)**

Connect to PostgreSQL and create the database:

```bash
# Try connecting as postgres user (you'll be prompted for password)
psql -U postgres

# Once connected, run:
CREATE DATABASE edunova_db;
\q
```

**Option B: If you don't know the postgres password**

1. Try connecting without specifying user (uses your system user):
   ```bash
   psql postgres
   ```
   Then create the database:
   ```sql
   CREATE DATABASE edunova_db;
   \q
   ```

2. Update your `.env` file to use your system username:
   ```env
   DB_USER=vanshmehta  # or your system username
   DB_PASSWORD=        # leave empty if no password
   ```

**Option C: Create a new PostgreSQL user (if needed)**

```bash
psql -U postgres
```

Then in psql:
```sql
CREATE USER edunova_user WITH PASSWORD 'your_password_here';
CREATE DATABASE edunova_db OWNER edunova_user;
GRANT ALL PRIVILEGES ON DATABASE edunova_db TO edunova_user;
\q
```

Update your `.env`:
```env
DB_USER=edunova_user
DB_PASSWORD=your_password_here
```

**Troubleshooting:**

- If you get "password authentication failed", you may need to reset the postgres password or use your system user
- On macOS, you can also try: `psql postgres` (without -U flag)
- Make sure PostgreSQL is running: `pg_isready`

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication Endpoints

#### Register User
- **POST** `/api/auth/register/`
- **Body:**
  ```json
  {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }
  ```
- **Response:**
  ```json
  {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "",
      "last_name": "",
      "profile": {
        "full_name": "John Doe"
      }
    },
    "tokens": {
      "refresh": "...",
      "access": "..."
    },
    "message": "User registered successfully"
  }
  ```

#### Login
- **POST** `/api/auth/login/`
- **Body:**
  ```json
  {
    "username": "johndoe",
    "password": "securepassword123"
  }
  ```
- **Response:**
  ```json
  {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "",
      "last_name": "",
      "profile": {
        "full_name": "John Doe"
      }
    },
    "tokens": {
      "refresh": "...",
      "access": "..."
    },
    "message": "Login successful"
  }
  ```

#### Get Current User
- **GET** `/api/auth/me/`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "",
    "last_name": "",
    "profile": {
      "full_name": "John Doe"
    }
  }
  ```

#### Refresh Token
- **POST** `/api/auth/token/refresh/`
- **Body:**
  ```json
  {
    "refresh": "<refresh_token>"
  }
  ```
- **Response:**
  ```json
  {
    "access": "<new_access_token>"
  }
  ```

## Frontend Integration

### Using with React

Include the access token in API requests:

```javascript
fetch('http://localhost:8000/api/auth/me/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

### CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (Create React App default)

To add more origins, update `CORS_ALLOWED_ORIGINS` in `edunova_backend/settings.py`.

## Project Structure

```
edunova_backend/
├── accounts/              # Authentication app
│   ├── models.py         # Profile model
│   ├── serializers.py    # API serializers
│   ├── views.py          # API views
│   ├── urls.py           # URL routing
│   └── signals.py        # Profile auto-creation
├── edunova_backend/      # Project settings
│   ├── settings.py       # Django settings
│   └── urls.py           # Root URL config
├── manage.py
├── requirements.txt
└── .env.example
```

## Development

### Running Tests

```bash
python manage.py test
```

### Accessing Admin Panel

Visit `http://localhost:8000/admin/` after creating a superuser.

## Production Considerations

1. Set `DEBUG=False` in production
2. Use a strong `SECRET_KEY`
3. Configure proper `ALLOWED_HOSTS`
4. Use environment-specific database credentials
5. Set up proper CORS origins for production domain
6. Use HTTPS in production
7. Configure proper JWT token lifetimes


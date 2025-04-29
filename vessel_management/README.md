# Vessel Management System API

This Django REST API serves as the backend for a vessel management system, providing endpoints for authentication, vessel management, file management, and system logging.

## Features

- JWT Authentication with role-based access control
- User management (registration, login, password reset)
- Vessel information management
- File upload and management
- System logging
- API documentation with Swagger/OpenAPI

## Requirements

- Python 3.8+
- PostgreSQL
- SendGrid Account (for email notifications)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd vessel-management-api
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database settings
   DB_NAME=vessel_management
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   
   # Email settings
   SENDGRID_API_KEY=your_sendgrid_api_key
   DEFAULT_FROM_EMAIL=your_email@example.com
   
   # Frontend URL for password reset links
   FRONTEND_URL=http://localhost:4200
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the API documentation at `http://localhost:8000/swagger/`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register/`: Register a new user
- `POST /api/v1/auth/login/`: Log in and obtain JWT tokens
- `POST /api/v1/auth/token/refresh/`: Refresh JWT token
- `GET /api/v1/auth/profile/`: Get user profile
- `PUT /api/v1/auth/profile/`: Update user profile
- `POST /api/v1/auth/password-reset/request/`: Request password reset
- `POST /api/v1/auth/password-reset/confirm/`: Confirm password reset
- `POST /api/v1/auth/password/change/`: Change password

### Vessels

- `GET /api/v1/vessels/`: List all vessels
- `POST /api/v1/vessels/`: Create a new vessel
- `GET /api/v1/vessels/{id}/`: Get vessel details
- `PUT /api/v1/vessels/{id}/`: Update vessel
- `DELETE /api/v1/vessels/{id}/`: Delete vessel

### Files

- `GET /api/v1/files/`: List all files
- `POST /api/v1/files/`: Upload a new file
- `GET /api/v1/files/{id}/`: Get file details
- `PUT /api/v1/files/{id}/`: Update file metadata
- `DELETE /api/v1/files/{id}/`: Delete file

### System Logs

- `GET /api/v1/logs/`: List all system logs
- `GET /api/v1/logs/{id}/`: Get log details

## Role-Based Access Control

- **Admin**: Full access to all features
- **Fleet Manager**: Manage vessels and related information
- **Crew Member**: View vessels and related information, limited edit capabilities

## Future Extensions

This core framework is designed to be extended with additional modules:
- Maintenance management
- Crew management
- Document management
- Voyage management
- Inventory/spare parts management

## License

[Specify your license] 
# Frontend - Course Management Platform

This is the frontend application for the Course Management Platform built with **Flask** and **Jinja2**.

## Features

- **User Authentication**: Login and Registration for Students, Instructors, Administrators, and Data Analysts
- **Role-Based Forms**: Dynamic forms that show role-specific fields
- **Responsive Design**: Mobile-friendly interface
- **Session Management**: Secure session handling with token-based authentication
- **Modern UI**: Clean and intuitive user interface

## Tech Stack

- **Backend Framework**: Flask
- **Templating**: Jinja2
- **Styling**: CSS3
- **Frontend Logic**: Vanilla JavaScript
- **HTTP Client**: Python Requests

## Project Structure

```
frontend/
├── app.py                     # Flask application entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── services/
│   └── auth_service.py       # Authentication API calls
├── templates/
│   ├── base.html             # Base template (navbar, footer)
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── dashboard.html        # User dashboard
│   ├── 404.html              # 404 error page
│   └── 500.html              # 500 error page
└── static/
    ├── css/
    │   └── style.css         # Main stylesheet
    └── js/
        └── main.js           # Utility functions and API client
```

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup Steps

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** (copy from template):
   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # macOS/Linux
   ```

5. **Update `.env` with your settings** (if needed):
   ```
   BACKEND_URL=http://127.0.0.1:8000
   SECRET_KEY=your-secret-key-here
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

The application will start at `http://localhost:5000`

### With Flask CLI

```bash
flask run
```

### Production Mode

For production, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Pages

### Login (`/login`)
- Email and password authentication
- Form validation
- Error messages
- Link to registration

### Register (`/register`)
- Create new user account
- Role selection (Student, Instructor, Administrator, Data Analyst)
- Optional fields for additional information
- Role-specific form fields
- Input validation

### Dashboard (`/dashboard`)
- User welcome message
- Display user ID and role
- Protected route (requires authentication)

## API Integration

The frontend communicates with the FastAPI backend at `http://127.0.0.1:8000`.

### Authentication Endpoints

- **Register**: `POST /auth/register`
  - Request: `{ name, email, password, role, ...optional fields }`
  - Response: User information

- **Login**: `POST /auth/login`
  - Request: `{ email, password }`
  - Response: `{ access_token, token_type, user_id, role }`

- **Get Current User**: `GET /auth/me`
  - Headers: `Authorization: Bearer {token}`
  - Response: User information

## Security Features

- **Session Management**: Secure Flask session handling
- **Token Storage**: Tokens stored in server-side sessions
- **CSRF Protection**: Token-based CSRF protection
- **Input Validation**: Client and server-side validation
- **Password Requirements**: Minimum 6 characters
- **Email Validation**: RFC-compliant email validation

## Styling

The application uses a modern, clean design with:
- **Color Scheme**: Professional blue primary color
- **Responsive Layout**: Adapts to all screen sizes
- **Smooth Animations**: Subtle transitions and animations
- **Accessibility**: Semantic HTML, proper labels, and ARIA attributes

### CSS Variables

Color variables defined in `static/css/style.css`:
- `--primary-color`: #007bff (Blue)
- `--secondary-color`: #6c757d (Gray)
- `--success-color`: #28a745 (Green)
- `--danger-color`: #dc3545 (Red)
- `--warning-color`: #ffc107 (Yellow)

## JavaScript Utilities

The `main.js` file provides utility functions:

### Utils
- `showToast(message, type)`: Display a notification
- `formatDate(date)`: Format date to readable format
- `validateEmail(email)`: Validate email format
- `deepCopy(obj)`: Deep copy an object

### API Client
- `API.get(url, options)`: Make GET request
- `API.post(url, data, options)`: Make POST request
- `API.put(url, data, options)`: Make PUT request
- `API.delete(url, options)`: Make DELETE request

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | http://127.0.0.1:8000 | Backend API URL |
| `SECRET_KEY` | dev-secret-key-... | Flask session secret key |
| `FLASK_ENV` | development | Flask environment |

## Troubleshooting

### Backend Connection Error
- Ensure backend is running on http://127.0.0.1:8000
- Check `BACKEND_URL` in `.env` file

### Session Expiration
- Sessions expire after 7 days of inactivity
- User will be redirected to login page

### Form Validation Issues
- Check browser console for JavaScript errors
- Ensure all required fields are filled
- Password must be at least 6 characters

## Future Enhancements

- [ ] Password reset functionality
- [ ] User profile management
- [ ] Course browsing and enrollment
- [ ] Course content viewing
- [ ] Student progress tracking
- [ ] Instructor course management
- [ ] Admin dashboard
- [ ] Email notifications

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is part of the Online Course Management Platform DBMS Assignment.

## Support

For issues or questions, please contact the development team or create an issue in the repository.

# Instructor Dashboard System

## Overview

A complete instructor dashboard system for managing courses, tracking analytics, uploading content, and viewing student insights in the Online Course Management Platform (OCMP).

---

## Features

### 1. **Instructor Dashboard Overview**
- Welcome banner with instructor name and ID
- Teaching statistics (courses, students, enrollment metrics)
- Real-time completion rate
- Interactive charts for visualization:
  - Students per course (bar chart)
  - Course completion status (doughnut chart)
- Quick access buttons for common actions

### 2. **Courses Teaching Section**
- Display all assigned courses
- Course cards showing:
  - Course title, level, category
  - Student enrollment count
  - Course completion statistics
  - Interactive action buttons
- Hover effects for better user experience

### 3. **Course Detail View**
- Comprehensive course information
- Tabbed interface with:
  - **Overview**: Course description and key metrics
  - **Content**: Course materials and upload system
  - **Students**: Enrolled student list with progress status
  - **Reviews**: Student feedback and ratings
  - **Analytics**: Detailed course analytics with charts

### 4. **Content Upload System**
- Dedicated upload page
- Form validation
- Supported content types:
  - Video lectures
  - Documents/Articles
  - Presentations
  - Quizzes
  - Exercises
  - Resources
- Topic association (optional)
- Error handling and user feedback

### 5. **Analytics Dashboard**
- Course enrollment breakdown
- Student completion statistics
- Average ratings
- Dropout rate tracking
- Visual charts for data representation

---

## File Structure

### Backend Changes

```
backend/app/repositories/
├── participation_repo.py (NEW: get_courses_by_instructor)

backend/app/services/
├── participation_service.py (NEW: get_instructor_courses_service)

backend/app/routers/
├── teaching.py (NEW: GET /teaching/instructor/{instructor_user_id})
```

### Frontend Changes

```
frontend/
├── templates/
│   ├── instructor_dashboard.html (NEW)
│   ├── instructor_course_detail.html (NEW)
│   ├── upload_content.html (NEW)
│   └── base.html (MODIFIED: navbar)
│
├── services/
│   └── instructor_service.py (NEW)
│
└── app.py (MODIFIED: added instructor routes)
```

---

## API Endpoints

### New Backend Endpoint

**GET** `/teaching/instructor/{instructor_user_id}`
- Retrieves all courses taught by an instructor
- Returns course details with enrollment statistics
- Example response:
```json
[
  {
    "course_id": 1,
    "course_title": "Python 101",
    "category": "Programming",
    "level": "Beginner",
    "duration": 40,
    "description": "Introduction to Python",
    "role_in_course": "Instructor",
    "assigned_date": "2024-01-15",
    "enrollment_count": 25,
    "completion_count": 18
  }
]
```

### Existing Endpoints Used

- `GET /auth/me` - Get current user
- `GET /analytics/instructors/{user_id}` - Get instructor stats
- `GET /courses/{course_id}` - Get course details
- `GET /analytics/courses/{course_id}` - Get course analytics
- `GET /content/course/{course_id}` - Get course content
- `GET /topics/courses/{course_id}/topics` - Get course topics
- `GET /enrollments/reviews/{course_id}` - Get course reviews
- `POST /content/upload` - Upload course content

---

## Flask Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/instructor/dashboard` | GET | Main instructor dashboard |
| `/instructor/course/<course_id>` | GET | Course detail view |
| `/instructor/course/<course_id>/upload` | GET | Upload content for specific course |
| `/instructor/upload-content` | GET | Upload content (no course selected) |
| `/instructor/course/<course_id>/analytics` | GET | Course analytics view |
| `/api/upload-content` | POST | API for content upload |

---

## Service Layer (Frontend)

**Location**: `frontend/services/instructor_service.py`

### Methods

```python
class InstructorService:
    # Authentication & User
    get_current_instructor(token)
    
    # Analytics
    get_instructor_analytics(user_id, token)
    recompute_instructor_stats(user_id, token)
    get_course_analytics(course_id, token)
    
    # Courses
    get_instructor_courses(user_id, token)
    get_course_details(course_id, token)
    
    # Content
    get_course_content(course_id, token)
    upload_content(payload, token)
    get_course_topics(course_id, token)
    
    # Reviews
    get_course_reviews(course_id, token)
    
    # Enrollments
    get_course_enrollments(course_id, token)
```

---

## UI/UX Design Details

### Color Scheme
- **Primary**: Purple (#8B5CF6) - Instructor-specific branding
- **Secondary**: Gradient backgrounds for headers
- **Accent**: Green (#10B981) for success, Orange (#F59E0B) for actions

### Components
- **Stat Cards**: Show key metrics with hover effects
- **Course Cards**: Display course information with action buttons
- **Tabs Interface**: Organized content presentation
- **Charts**: Chart.js for visual analytics
- **Forms**: Clean, accessible form design with validation

### Responsive Design
- Mobile-friendly layouts
- Tablet and desktop optimized
- Touch-friendly buttons

---

## Authentication & Security

1. **JWT Token Required**: All routes check for valid JWT token
2. **Role-based Access**: Navbar shows instructor dashboard for instructors
3. **User Validation**: Backend validates instructor ownership before operations
4. **CORS**: Requests include Authorization headers
5. **Session Management**: Flask sessions store token and user details

---

## Data Flow

### Dashboard Load Flow
```
1. User navigates to /instructor/dashboard
2. Check JWT token (if missing → redirect to login)
3. Fetch current user info via GET /auth/me
4. Fetch instructor analytics via GET /analytics/instructors/{user_id}
5. Fetch teaching assignments via GET /teaching/instructor/{user_id}
6. Calculate derived metrics (active enrollments, completion rate)
7. Prepare chart data
8. Render template with all data
```

### Content Upload Flow
```
1. User navigates to /instructor/course/{course_id}/upload
2. Fetch instructor's courses
3. Display upload form
4. User fills form and submits
5. POST /api/upload-content (backend validates)
6. Backend creates CourseContent record
7. Redirect to course detail page
8. User sees newly uploaded content
```

---

## Database Models Used

### Backend (SQLAlchemy)
- `User` - User accounts
- `Instructor` - Instructor profile
- `Course` - Course information
- `Teaching` - Instructor-Course relationship
- `Enrollment` - Student enrollment
- `CourseContent` - Course materials
- `Statistics` - Course statistics
- `InstructorStatistics` - Instructor-level stats

### Key Relationships
```
Instructor → Teaching → Course
                     ↓
                 Enrollment → Student
                 CourseContent
                 Statistics
```

---

## Error Handling

### Frontend Validation
- Required field checking
- URL validation for file links
- User feedback for failed uploads

### Backend Validation
- User existence checks
- Role-based authorization
- Duplicate enrollment prevention
- Course access validation

### Error Messages
- Clear, user-friendly messages
- Automatic error dismissal
- Flash messages for redirects

---

## Performance Optimizations

1. **Lazy Loading**: Chart.js only initializes when tab is opened
2. **Efficient Queries**: Repository functions use optimized SQLAlchemy queries
3. **Caching**: Statistics can be recomputed on-demand
4. **Batch Operations**: Multiple course data fetched in single requests

---

## Testing Checklist

- [ ] Login as instructor user
- [ ] Verify instructor dashboard loads
- [ ] Check all stat cards display correctly
- [ ] Verify chart rendering
- [ ] Test course detail view
- [ ] Test content upload with different types
- [ ] Verify reviews display
- [ ] Check analytics calculations
- [ ] Test responsive design on mobile
- [ ] Verify navigation between pages
- [ ] Check error messages for invalid data

---

## Future Enhancements

1. **Bulk Upload**: CSV import for multiple students
2. **Announcements**: Send notifications to enrolled students
3. **Gradebook**: Track and manage student grades
4. **Attendance Tracking**: Record student participation
5. **Email Notifications**: Alert students for new content
6. **Video Streaming**: Integrated video player
7. **Discussion Forums**: Student-instructor communication
8. **Assignment Grading**: In-platform grading system
9. **Certificate Generation**: Auto-generate completion certificates
10. **Advanced Analytics**: Predictive analysis for dropout risk

---

## Configuration

### Environment Variables
```
BACKEND_URL=http://127.0.0.1:8000
FLASK_ENV=development
FLASK_DEBUG=1
SESSION_TYPE=filesystem
```

### Backend Configuration
- Database: SQLite (default) or PostgreSQL
- JWT Secret: Configure in core/security.py
- API Timeout: 10 seconds (configurable)

---

## Troubleshooting

### Common Issues

**1. "No courses assigned" message**
- Verify instructor is assigned to courses in database
- Check Teaching table for records
- Ensure user role is "Instructor"

**2. Analytics not updating**
- Run `/analytics/recompute/instructor/{user_id}` endpoint
- Check event listeners for enrollment updates
- Verify statistics calculation logic

**3. Content upload fails**
- Check file URL is accessible
- Verify course_id is correct
- Ensure instructor is assigned to course
- Check request payload format

**4. Charts not displaying**
- Verify Chart.js CDN is loaded
- Check browser console for errors
- Ensure canvas elements have IDs
- Validate JSON data format

---

## Support

For issues or questions:
1. Check this documentation
2. Review Flask app.py for route details
3. Check browser console for JavaScript errors
4. Review backend logs for API errors
5. Contact development team

---

## Version History

- **v1.0.0** - Initial release with core dashboard features
  - Instructor dashboard
  - Course management
  - Content upload
  - Analytics display
  - Review system

---

## License

Part of the Online Course Management Platform (OCMP) project.

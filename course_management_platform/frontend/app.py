from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_session import Session
from config import DevelopmentConfig
from services.auth_service import AuthService
from services.course_service import CourseService
from services.dashboard_service import DashboardService
from services.instructor_service import InstructorService
from services.admin_service import AdminService
from services.analyst_service import AnalystService
from services.progress_service import ProgressService
import json
from datetime import datetime
import os
import requests

# Backend URL (used to query server instance)
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
Session(app)

# Authentication Routes
@app.route('/')
def index():
    """Home / Landing page - shows course discovery"""
    # Fetch courses from backend
    success, courses = CourseService.get_all_courses()

    if not success:
        courses = []

    # Fetch categories for filtering
    cat_success, categories = CourseService.get_all_categories()
    if not cat_success:
        categories = []

    return render_template('home.html', courses=courses, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        success, response = AuthService.login(email, password)
        
        if success:
            # Store token and user info in session
            session['token'] = response.get('access_token')
            session['user_id'] = response.get('user_id')
            session['role'] = response.get('role')
            session['admin_level'] = response.get('admin_level')  # Store admin level if present
            session.permanent = True
            
            print(f"DEBUG login - Response admin_level: {response.get('admin_level')}, Role: {response.get('role')}")
            print(f"DEBUG login - Session set with admin_level: {session.get('admin_level')}")
            
            # Determine redirect based on user role and admin level
            user_role = (response.get('role') or '').lower()
            if 'instructor' in user_role:
                redirect_url = '/instructor/dashboard'
            elif 'analyst' in user_role:
                redirect_url = '/analyst/dashboard'
            elif user_role == 'administrator':
                # Check admin level
                admin_level = (response.get('admin_level') or '').lower()
                print(f"DEBUG login - Admin detected, admin_level: {admin_level}")
                if admin_level == 'senior':
                    redirect_url = '/admin/senior/dashboard'
                    print(f"DEBUG login - Senior admin, redirecting to /admin/senior/dashboard")
                else:
                    redirect_url = '/admin/dashboard'
                    print(f"DEBUG login - Junior admin, redirecting to /admin/dashboard")
            else:
                redirect_url = '/dashboard'
            
            # Return token in response for client storage
            # Also store current backend instance id in session so we can detect restarts
            try:
                r = requests.get(f"{BACKEND_URL}/server/instance", timeout=2)
                if r.ok:
                    data = r.json()
                    session['server_instance_id'] = data.get('instance_id')
            except Exception:
                # Don't block login if instance endpoint is unavailable
                pass
            return jsonify({
                'success': True, 
                'redirect': redirect_url,
                'access_token': response.get('access_token'),
                'user_id': response.get('user_id'),
                'role': response.get('role'),
                'admin_level': response.get('admin_level')
            }), 200
        else:
            error_msg = response.get('error') or response.get('detail', 'Login failed')
            return jsonify({'error': error_msg}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate password length
        if len(data.get('password', '')) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        success, response = AuthService.register(data)
        
        if success:
            return jsonify({'success': True, 'message': 'Registration successful! Please login.'}), 200
        else:
            error_msg = response.get('error') or response.get('detail', 'Registration failed')
            return jsonify({'error': error_msg}), 400
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page - requires authentication"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    # Check if user is admin - redirect to admin dashboard
    user_role = session.get('role', '').lower()
    if user_role == 'administrator':
        return redirect(url_for('admin_dashboard'))
    
    # Check if user is instructor - redirect to instructor dashboard
    if user_role == 'instructor':
        return redirect(url_for('instructor_dashboard'))
    
    # Check if user is data analyst - redirect to analyst dashboard
    if user_role == 'data analyst':
        return redirect(url_for('data_analyst_dashboard'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch current user info
    user_success, user_data = DashboardService.get_current_user(token)
    
    # IMPORTANT: Only recompute student statistics for Student role
    # This avoids attempting to create StudentStatistics for non-student users
    if session.get('role', '').lower() == 'student':
        DashboardService.recompute_student_stats(user_id, token)
    
    # Fetch student analytics (now updated)
    analytics_success, analytics = DashboardService.get_student_analytics(user_id, token)
    
    # Fetch student enrollments (detailed course info)
    enrollments_success, enrollments = DashboardService.get_student_enrollments(user_id, token)
    
    if not user_success:
        flash('Failed to fetch user data. Please login again.', 'danger')
        return redirect(url_for('login'))
    
    # Prepare stats data
    stats = {
        'total_enrollments': 0,
        'completed_courses': 0,
        'ongoing_courses': 0,
        'enrolled_courses': []
    }
    
    if analytics_success and analytics:
        stats.update(analytics)
        # Map active_courses to ongoing_courses for template compatibility
        if 'active_courses' in stats:
            stats['ongoing_courses'] = stats.pop('active_courses')
    
    # Add enrolled courses to stats
    if enrollments_success and enrollments:
        stats['enrolled_courses'] = enrollments
    
    user_context = {
        'name': user_data.get('name') if user_success else session.get('user_id'),
        'user_id': user_id
    }
    
    return render_template('dashboard.html', user=user_context, stats=stats)


# Before each request, verify backend instance hasn't changed; if it has, clear session and force login
@app.before_request
def check_server_instance():
    # Only enforce when user has an active session
    if 'token' not in session:
        return None

    # Skip static files
    if request.path.startswith('/static/'):
        return None

    # Attempt to query backend instance id
    try:
        resp = requests.get(f"{BACKEND_URL}/server/instance", timeout=1.5)
        if not resp.ok:
            return None
        data = resp.json()
        instance_id = data.get('instance_id')
        if not instance_id:
            return None
        # If session doesn't have stored instance, set it
        if 'server_instance_id' not in session:
            session['server_instance_id'] = instance_id
            return None

        # If instance differs, invalidate session and inform user
        if session.get('server_instance_id') != instance_id:
            # clear session and redirect to login with message
            session.clear()
            # For AJAX/API requests, return JSON error
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'error': 'Session expired. Please login again.'}), 401
            flash('Session expired. Please login again.', 'warning')
            return redirect(url_for('login'))
    except Exception:
        # If backend unreachable, don't log out (avoid lockout during short network hiccups)
        return None


@app.route('/enroll-courses')
def enroll_courses():
    """New enrollment page - shows all available courses"""
    if 'token' not in session:
        flash('Please login to enroll in courses', 'warning')
        return redirect(url_for('login'))
    
    # Fetch all available courses
    success, courses = DashboardService.get_all_courses()
    
    if not success:
        courses = []
    
    user_context = {
        'user_id': session.get('user_id')
    }
    
    return render_template('enroll_courses.html', courses=courses, user=user_context)


@app.route('/courses/<int:course_id>')
def course_detail(course_id: int):
    """Course detail page"""
    success, course = CourseService.get_course_by_id(course_id)
    content_success, content = CourseService.get_course_content(course_id)
    uni_success, university = CourseService.get_university_by_course(course_id)
    topics_success, topics = CourseService.get_topics_by_course(course_id)
    reviews_success, reviews = CourseService.get_public_reviews_by_course(course_id)

    if not success or not course:
        return render_template('404.html'), 404

    # Check if user is enrolled
    is_enrolled = False
    if 'token' in session and 'user_id' in session:
        token = session.get('token')
        user_id = session.get('user_id')
        enrolled_success, enrollments = ProgressService.get_enrollment(user_id, course_id, token)
        if enrolled_success and enrollments:
            is_enrolled = True

    # content/topics/university/reviews may be empty or None
    return render_template('course_detail.html', course=course, content=content if content_success else [], university=university if uni_success else None, topics=topics if topics_success else [], reviews=reviews if reviews_success else [], is_enrolled=is_enrolled)


@app.route('/enroll/<int:course_id>', methods=['POST'])
def enroll(course_id: int):
    """Enroll the current user in a course"""
    if 'token' not in session:
        flash('Please login to enroll', 'warning')
        return redirect(url_for('login'))

    student_user_id = session.get('user_id')
    token = session.get('token')

    if not student_user_id:
        flash('User information missing. Please login again.', 'danger')
        return redirect(url_for('login'))

    # Use DashboardService to enroll
    success, response = DashboardService.enroll_course(student_user_id, course_id, token)
    
    if success:
        flash('Enrollment successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        error_msg = response.get('detail') or response.get('error') or 'Enrollment failed'
        flash(error_msg, 'danger')
        return redirect(url_for('course_detail', course_id=course_id))


# ============================================================
# COURSE LEARNING & ASSESSMENT ROUTES
# ============================================================

@app.route('/course/<int:course_id>/learn')
def course_learn(course_id: int):
    """Course learning page with topic checklist"""
    if 'token' not in session:
        flash('Please login to view course', 'warning')
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch course details
    success, course = CourseService.get_course_by_id(course_id)
    if not success or not course:
        return render_template('404.html'), 404
    
    # Fetch course topics
    topics_success, topics = CourseService.get_topics_by_course(course_id)
    
    # Fetch course content
    content_success, course_content = InstructorService.get_course_content(course_id, token)
    
    if not content_success:
        course_content = []
    
    user_context = {
        'user_id': user_id
    }
    
    return render_template('course_learn.html', 
        course=course, 
        topics=topics if topics_success else [], 
        course_content=course_content,
        current_user=user_context, 
        auth_token=token
    )


@app.route('/course/<int:course_id>/assessment')
def course_assessment(course_id: int):
    """Course assessment page"""
    if 'token' not in session:
        flash('Please login to view assessment', 'warning')
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch course details
    success, course = CourseService.get_course_by_id(course_id)
    if not success or not course:
        return render_template('404.html'), 404
    
    user_context = {
        'user_id': user_id
    }
    
    return render_template('course_assessment.html', course=course, current_user=user_context, auth_token=token)


@app.route('/course/<int:course_id>/review', methods=['GET'])
def course_review(course_id: int):
    """Course review/rating page shown after completion/assessment"""
    if 'token' not in session:
        flash('Please login to leave a review', 'warning')
        return redirect(url_for('login'))

    token = session.get('token')
    user_id = session.get('user_id')

    # Fetch course details for context
    success, course = CourseService.get_course_by_id(course_id)
    if not success or not course:
        return render_template('404.html'), 404

    user_context = {
        'user_id': user_id
    }

    return render_template('course_review.html', course=course, current_user=user_context, auth_token=token)


@app.route('/api/progress/rate/<int:course_id>', methods=['POST'])
def api_rate_course(course_id: int):
    """API endpoint to accept rating from frontend and forward to backend"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    token = session.get('token')
    user_id = session.get('user_id')

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    rating = data.get('rating')
    review_text = data.get('review_text', '')
    is_public = data.get('is_public', False)

    if rating is None or not (1 <= int(rating) <= 5):
        return jsonify({'error': 'Invalid rating. Must be 1-5.'}), 400

    success, result = ProgressService.rate_course(user_id, course_id, int(rating), review_text, is_public=is_public, token=token)

    if success:
        return jsonify(result), 200
    else:
        # Normalize backend error payloads into a string message
        if isinstance(result, dict):
            msg = result.get('detail') or result.get('error') or str(result)
        else:
            msg = str(result)
        return jsonify({'error': msg}), 400


# ============================================================
# PROGRESS API ROUTES
# ============================================================

@app.route('/api/progress/topics/<int:course_id>')
def api_get_topics(course_id: int):
    """Get all topics for a course"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    success, topics = ProgressService.get_course_topics(course_id, token)
    
    if success:
        return jsonify(topics), 200
    else:
        return jsonify({'error': 'Failed to fetch topics'}), 400


@app.route('/api/progress/enrollment/<int:course_id>')
def api_get_enrollment(course_id: int):
    """Get enrollment data for current user and course"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    success, enrollment = ProgressService.get_enrollment(user_id, course_id, token)
    
    if success and enrollment:
        return jsonify(enrollment), 200
    else:
        return jsonify({'error': 'Enrollment not found'}), 404


@app.route('/api/progress/current-topic/<int:course_id>')
def api_get_current_topic(course_id: int):
    """Get current topic ID for current user in course"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    success, current_topic = ProgressService.get_current_topic(user_id, course_id, token)
    
    if success:
        return jsonify({'current_topic': current_topic}), 200
    else:
        return jsonify({'current_topic': None}), 200


@app.route('/api/progress/update/<int:course_id>/<int:topic_id>', methods=['PUT'])
def api_update_progress(course_id: int, topic_id: int):
    """Update topic progress for current user"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    success, result = ProgressService.update_progress(user_id, course_id, topic_id, token)
    
    if success:
        return jsonify(result), 200
    else:
        return jsonify({'error': result or 'Failed to update progress'}), 400


@app.route('/api/progress/rollback/<int:course_id>/<int:topic_id>', methods=['PUT'])
def api_rollback_progress(course_id: int, topic_id: int):
    """Rollback topic progress for current user (when unchecking)"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    success, result = ProgressService.rollback_progress(user_id, course_id, topic_id, token)
    
    if success:
        return jsonify(result), 200
    else:
        return jsonify({'error': result or 'Failed to rollback progress'}), 400


@app.route('/api/progress/reset/<int:course_id>', methods=['PUT'])
def api_reset_progress(course_id: int):
    """Reset progress to first topic for current user (when quiz is failed)"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    success, result = ProgressService.reset_progress(user_id, course_id, token)
    
    if success:
        return jsonify(result), 200
    else:
        return jsonify({'error': result or 'Failed to reset progress'}), 400


@app.route('/api/progress/submit/<int:course_id>', methods=['POST'])
def api_submit_assessment(course_id: int):
    """Submit assessment with either score or answers array"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    data = request.get_json() or {}
    score = data.get('score')
    answers = data.get('answers')
    
    if score is None and answers is None:
        return jsonify({'error': 'Either score or answers must be provided'}), 400
    
    if score is not None:
        score = int(score)
        if not (0 <= score <= 100):
            return jsonify({'error': 'Invalid score. Must be between 0 and 100.'}), 400
    
    success, result = ProgressService.submit_assessment(user_id, course_id, score=score, answers=answers, token=token)
    
    if success:
        return jsonify(result), 200
    else:
        # Normalize backend error payloads into a string message
        if isinstance(result, dict):
            msg = result.get('detail') or result.get('error') or str(result)
        else:
            msg = str(result)
        return jsonify({'error': msg}), 400


# ============================================================
# INSTRUCTOR ROUTES
# ============================================================

@app.route('/instructor/dashboard')
def instructor_dashboard():
    """Instructor dashboard - shows courses and analytics"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch current instructor info
    user_success, user_data = InstructorService.get_current_instructor(token)
    
    if not user_success:
        flash('Failed to fetch user data. Please login again.', 'danger')
        return redirect(url_for('login'))
    
    # Recompute instructor statistics
    InstructorService.recompute_instructor_stats(user_id, token)
    
    # Fetch instructor analytics
    analytics_success, analytics = InstructorService.get_instructor_analytics(user_id, token)
    
    # Fetch courses taught by instructor
    courses_success, instructor_courses = InstructorService.get_instructor_courses(user_id, token)
    
    # Fetch pending courses created by instructor
    pending_success, pending_courses = CourseService.get_instructor_pending_courses(token)
    if not pending_success:
        pending_courses = []
    
    stats = {
        'total_courses_taught': 0,
        'total_students': 0
    }
    
    if analytics_success and analytics:
        stats.update(analytics)
    
    if not courses_success:
        instructor_courses = []
    
    # Calculate total enrollments, active enrollments, and completion rate
    total_enrollments = 0
    active_enrollments = 0
    completed = 0
    
    if instructor_courses:
        for course in instructor_courses:
            # Total enrollments across all courses
            total_enrollments += course.get('enrollment_count', 0)
            # Completed enrollments across all courses
            completed += course.get('completion_count', 0)
    
    # Active enrollments = total - completed
    active_enrollments = total_enrollments - completed
    completion_rate = int((completed / total_enrollments * 100) if total_enrollments > 0 else 0)
    
    # Prepare chart data
    course_stats_data = {
        'labels': [c.get('course_title', 'Untitled')[:20] for c in instructor_courses] if instructor_courses else [],
        'data': [c.get('enrollment_count', 0) for c in instructor_courses] if instructor_courses else []
    }
    
    completion_stats_data = {
        'labels': ['Completed', 'In Progress', 'Pending'],
        'data': [completed, active_enrollments, 0]
    }
    
    user_context = {
        'name': user_data.get('name', 'Instructor'),
        'user_id': user_id
    }
    
    return render_template('instructor_dashboard.html',
        user=user_context,
        stats=stats,
        instructor_courses=instructor_courses,
        pending_courses=pending_courses,
        total_enrollments=total_enrollments,
        active_enrollments=active_enrollments,
        completion_rate=completion_rate,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        course_stats_json=json.dumps(course_stats_data),
        completion_stats_json=json.dumps(completion_stats_data)
    )


@app.route('/instructor/create-course', methods=['GET', 'POST'])
def instructor_create_course():
    """Create a new course as an instructor"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch current instructor info
    user_success, user_data = InstructorService.get_current_instructor(token)
    
    if not user_success:
        flash('Failed to fetch user data. Please login again.', 'danger')
        return redirect(url_for('login'))
    
    # Fetch universities for dropdown
    uni_success, universities = CourseService.get_all_universities()
    if not uni_success:
        universities = []
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Course title is required'}), 400
        
        # Topics are now optional - can be added later during course editing
        topics = data.get('topics', [])
        
        # Prepare course data - only pass fields that are present
        course_data = {
            'title': data.get('title'),
            'topics': topics  # Empty list is acceptable
        }
        
        # Add optional fields only if they're present and not empty
        if data.get('description'):
            course_data['description'] = data['description']
        if data.get('category'):
            course_data['category'] = data['category']
        if data.get('level'):
            course_data['level'] = data['level']
        if data.get('language'):
            course_data['language'] = data['language']
        if data.get('duration') is not None:
            course_data['duration'] = data['duration']
        if data.get('university_id') is not None:
            course_data['university_id'] = data['university_id']
        
        # Add quiz questions if provided
        quiz_questions = data.get('quiz_questions', [])
        if quiz_questions:
            course_data['quiz_questions'] = quiz_questions
        
        # Log the data being sent (for debugging)
        print(f"[DEBUG] Course data being sent to backend: {course_data}")
        
        # Create course via API
        success, response = CourseService.create_instructor_course(course_data, token)
        
        if success:
            course_id = response.get('course_id') or response.get('id')
            flash(f'Course "{course_data["title"]}" created successfully! It is now pending approval.', 'success')
            return jsonify({'success': True, 'message': 'Course created successfully', 'course_id': course_id, 'redirect': url_for('instructor_dashboard')}), 201
        else:
            # Extract error details from response
            error_msg = response.get('error') or response.get('detail', 'Failed to create course')
            if isinstance(error_msg, list):
                error_msg = ', '.join([str(e) for e in error_msg])
            print(f"[DEBUG] Backend error response: {response}")
            return jsonify({'error': error_msg}), 400
    
    # GET request - show the form
    user_context = {
        'name': user_data.get('name', 'Instructor'),
        'user_id': user_id
    }
    
    return render_template('instructor_course_creation.html',
        user=user_context,
        universities=universities
    )


@app.route('/instructor/course/<int:course_id>')
def instructor_course_detail(course_id: int):
    """Instructor course detail view"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch course details
    course_success, course = InstructorService.get_course_details(course_id, token)
    
    if not course_success:
        flash('Course not found', 'warning')
        return redirect(url_for('instructor_dashboard'))
    
    # Fetch course analytics
    analytics_success, analytics = InstructorService.get_course_analytics(course_id, token)
    
    # Fetch course content
    content_success, content = InstructorService.get_course_content(course_id, token)
    
    # Fetch course topics
    topics_success, topics = InstructorService.get_course_topics(course_id, token)
    
    # Fetch course reviews
    reviews_success, reviews = InstructorService.get_course_reviews(course_id, token)
    
    analytics_data = {
        'total_enrollments': 0,
        'completed_students': 0,
        'active_students': 0,
        'pending_students': 0,
        'average_rating': 'N/A',
        'completion_rate': 0,
        'dropout_rate': 0,
        'dropout_count': 0
    }
    
    if analytics_success and analytics:
        analytics_data.update(analytics)
    
    if not content_success:
        content = []
    
    if not topics_success:
        topics = []
    
    if not reviews_success:
        reviews = []
    
    # Fetch enrolled students (instructor-scoped) via service (handle wrapper response)
    students_success, students_resp = InstructorService.get_course_students(course_id, token)
    if students_success and students_resp:
        if isinstance(students_resp, dict) and 'students' in students_resp:
            enrolled_students = students_resp.get('students') or []
        elif isinstance(students_resp, list):
            enrolled_students = students_resp
        else:
            enrolled_students = []
    else:
        enrolled_students = []

    return render_template('instructor_course_detail.html',
        course=course,
        analytics=analytics_data,
        course_content=content,
        topics=topics,
        course_reviews=reviews,
        enrolled_students=enrolled_students,
        user={'user_id': user_id},
        token=token
    )


@app.route('/instructor/course/<int:course_id>/analytics')
def instructor_course_analytics(course_id: int):
    """Instructor course analytics view"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    
    # Fetch course details
    course_success, course = InstructorService.get_course_details(course_id, token)
    
    if not course_success:
        flash('Course not found', 'warning')
        return redirect(url_for('instructor_dashboard'))
    
    # Fetch course analytics
    analytics_success, analytics = InstructorService.get_course_analytics(course_id, token)
    
    # Redirect to detail tab
    return redirect(url_for('instructor_course_detail', course_id=course_id))


@app.route('/instructor/course/<int:course_id>/upload')
def instructor_upload_content(course_id):
    """Content upload page for a specific course"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch instructor courses
    courses_success, instructor_courses = InstructorService.get_instructor_courses(user_id, token)
    
    if not courses_success:
        instructor_courses = []
    
    selected_course_title = None
    course_topics = []
    
    # Fetch topics for the selected course
    if course_id and instructor_courses:
        for course in instructor_courses:
            if course.get('course_id') == course_id:
                selected_course_title = course.get('course_title')
                break
        
        # Fetch topics for the selected course
        topics_success, topics = InstructorService.get_course_topics(course_id, token)
        if topics_success and topics:
            course_topics = topics if isinstance(topics, list) else topics.get('topics', [])
    
    return render_template('upload_content.html',
        instructor_courses=instructor_courses,
        course_id=course_id,
        selected_course_title=selected_course_title,
        course_topics=course_topics,
        user={'user_id': user_id}
    )


@app.route('/instructor/upload-content')
def instructor_upload_content_base():
    """Content upload page without course selected"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch instructor courses
    courses_success, instructor_courses = InstructorService.get_instructor_courses(user_id, token)
    
    if not courses_success:
        instructor_courses = []
    
    return render_template('upload_content.html',
        instructor_courses=instructor_courses,
        course_id=None,
        selected_course_title=None,
        course_topics=[],
        user={'user_id': user_id}
    )



@app.route('/api/upload-content', methods=['POST'])
def api_upload_content():
    """API endpoint for uploading content"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    token = session.get('token')
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Validate required fields
    required = ['course_id', 'title', 'content_type', 'file_url']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    # Ensure instructor_user_id is set
    if 'instructor_user_id' not in data:
        data['instructor_user_id'] = session.get('user_id')
    
    # Call backend API
    success, response = InstructorService.upload_content(data, token)
    
    if success:
        return jsonify({'success': True, 'data': response}), 200
    else:
        error_msg = response.get('error') or response.get('detail') or 'Upload failed'
        return jsonify({'success': False, 'error': error_msg}), 400


@app.route('/api/courses/<int:course_id>/topics', methods=['GET'])
def api_get_course_topics(course_id):
    """API endpoint for fetching topics of a course"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    token = session.get('token')
    
    # Fetch topics for the course
    success, topics = InstructorService.get_course_topics(course_id, token)
    
    if success and topics:
        # Handle different response formats
        if isinstance(topics, list):
            return jsonify({'success': True, 'topics': topics}), 200
        elif isinstance(topics, dict) and 'topics' in topics:
            return jsonify({'success': True, 'topics': topics['topics']}), 200
        else:
            return jsonify({'success': True, 'topics': topics}), 200
    else:
        # Return empty list if no topics found
        return jsonify({'success': True, 'topics': []}), 200


@app.route('/instructor/course/<int:course_id>/edit', methods=['GET', 'POST'])
def instructor_edit_course(course_id: int):
    """Edit an approved course"""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Fetch course details
    course_success, course = CourseService.get_course_by_id(course_id)
    if not course_success or not course:
        flash('Course not found', 'warning')
        return redirect(url_for('instructor_dashboard'))
    
    # Check if course is approved and belongs to instructor
    if course.get('approval_status') != 'Approved':
        flash('Only approved courses can be edited', 'warning')
        return redirect(url_for('instructor_dashboard'))
    
    # Fetch course topics
    topics_success, topics = CourseService.get_topics_by_course(course_id)
    
    # Fetch course content
    content_success, course_content = InstructorService.get_course_content(course_id, token)
    
    # Fetch universities for dropdown
    uni_success, universities = CourseService.get_all_universities()
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Course title is required'}), 400
        
        # Prepare update data
        update_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'category': data.get('category'),
            'level': data.get('level'),
            'language': data.get('language'),
            'duration': data.get('duration'),
            'university_id': data.get('university_id')
        }
        
        # Call backend service to update course
        success, result = InstructorService.update_course(course_id, update_data, token)
        
        if success:
            return jsonify({'success': True, 'message': 'Course updated successfully'}), 200
        else:
            error_msg = result.get('error', 'Failed to update course') if isinstance(result, dict) else 'Failed to update course'
            return jsonify({'error': error_msg}), 500
    
    return render_template('instructor_edit_course.html',
        course=course,
        topics=topics if topics_success else [],
        course_content=course_content if content_success else [],
        universities=universities if uni_success else [],
        current_user={'user_id': user_id},
        auth_token=token
    )


@app.route('/api/course/<int:course_id>/topic', methods=['POST', 'DELETE'])
def api_manage_topic(course_id: int):
    """Add or delete a topic from a course"""
    if 'token' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    token = session.get('token')
    data = request.get_json()
    
    if request.method == 'POST':
        # Add topic
        if not data.get('name'):
            return jsonify({'error': 'Topic name is required'}), 400
        
        # Prepare topic data
        topic_data = {
            'name': data.get('name'),
            'description': data.get('description', '')
        }
        
        # Call backend to add topic to course
        success, result = InstructorService.add_topic_to_course(course_id, topic_data, token)
        
        if success:
            return jsonify({'success': True, 'message': 'Topic added successfully', 'data': result}), 201
        else:
            error_msg = result.get('error', 'Failed to add topic') if isinstance(result, dict) else 'Failed to add topic'
            return jsonify({'error': error_msg}), 500
    
    elif request.method == 'DELETE':
        # Delete topic
        topic_id = data.get('topic_id')
        if not topic_id:
            return jsonify({'error': 'Topic ID is required'}), 400
        
        # Call backend to delete topic
        success, result = InstructorService.delete_topic_from_course(course_id, topic_id, token)
        
        if success:
            return jsonify({'success': True, 'message': 'Topic deleted successfully'}), 200
        else:
            error_msg = result.get('error', 'Failed to delete topic') if isinstance(result, dict) else 'Failed to delete topic'
            return jsonify({'error': error_msg}), 500


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return render_template('logout.html')

# ============================================================
# ADMIN ROUTES (Requires Administrator role)
# ============================================================

def check_admin_role():
    """Middleware to check if user is admin"""
    if 'token' not in session:
        return False
    return session.get('role', '').lower() == 'administrator'

def check_senior_admin():
    """Middleware to check if user is Senior Admin"""
    if not check_admin_role():
        return False
    admin_level = (session.get('admin_level') or '').lower()
    return admin_level == 'senior'

def check_analyst_role():
    """Middleware to check if user is Data Analyst"""
    if 'token' not in session:
        return False
    return 'analyst' in (session.get('role') or '').lower()

@app.route('/admin/dashboard')
def admin_dashboard():
    """Main admin dashboard - Junior Admin OR redirect Senior to their dashboard"""
    if not check_admin_role():
        return redirect(url_for('login'))
    
    # Get token and decode to check admin_level
    token = session.get('token')
    admin_level_from_session = session.get('admin_level', '').lower()
    
    # Check both session and token for admin_level
    # Prefer session if available, decode token as fallback
    admin_level = admin_level_from_session or 'junior'
    
    print(f"DEBUG admin_dashboard - admin_level from session: {session.get('admin_level')}, admin_level_from_session: {admin_level_from_session}, final admin_level: {admin_level}")
    
    # Redirect senior admins to their dashboard
    if admin_level == 'senior':
        return redirect(url_for('senior_admin_dashboard'))
    
    # Get token from session and pass to template
    user_id = session.get('user_id')
    
    # Just serve the template - all data loading is done client-side
    return render_template('admin_dashboard.html', token=token, user_id=user_id, admin_level=admin_level)


@app.route('/admin/student-profile')
def admin_student_profile():
    """Student profile view for admins"""
    if not check_admin_role():
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    admin_level = session.get('admin_level', 'Junior')
    
    # Just serve the template - all data loading is done client-side
    return render_template('student_profile.html', token=token, user_id=user_id, admin_level=admin_level)


@app.route('/student-profile')
def student_profile_view():
    """Student profile view for non-admin users (instructors can use this)."""
    if 'token' not in session:
        return redirect(url_for('login'))

    token = session.get('token')
    user_id = session.get('user_id')

    # Serve same template as admin view but without admin guard
    return render_template('student_profile.html', token=token, user_id=user_id)


@app.route('/admin/senior/dashboard')
def senior_admin_dashboard():
    """Senior Admin Dashboard - with delete privileges"""
    if not check_admin_role():
        return redirect(url_for('login'))
    
    # Get admin_level from session
    admin_level = (session.get('admin_level') or '').lower()
    
    print(f"DEBUG senior_admin_dashboard - admin_level from session: {session.get('admin_level')}, admin_level: {admin_level}")
    
    # If not senior, redirect to junior dashboard
    if admin_level != 'senior':
        print(f"DEBUG senior_admin_dashboard - not senior, redirecting to admin_dashboard")
        flash('Access denied. Senior Admin privileges required.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Just serve the template - all data loading is done client-side
    return render_template('senior_admin_dashboard.html', token=token, user_id=user_id, admin_level=admin_level)


@app.route('/analyst/dashboard')
def data_analyst_dashboard():
    """Data Analyst Dashboard - Analytics and insights for all platform data"""
    if not check_analyst_role():
        return redirect(url_for('login'))
    
    token = session.get('token')
    user_id = session.get('user_id')
    
    # Get backend URL for frontend API calls
    backend_url = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')
    
    # Serve the template with backend URL
    return render_template('data_analyst_dashboard.html', token=token, user_id=user_id, backend_url=backend_url)


@app.route('/admin/courses')
def admin_courses():
    """Course management page"""
    if not check_admin_role():
        return redirect(url_for('login'))
    
    token = session.get('token')
    admin_level = session.get('admin_level', 'Junior')
    
    # Fetch courses and instructors
    courses_success, courses = AdminService.get_all_courses(token)
    instructors_success, instructors = AdminService.get_all_instructors(token)
    
    # Fetch instructors for each course
    course_instructors = {}
    if courses_success:
        for course in courses:
            instr_success, course_instrs = AdminService.get_instructors_by_course(course['course_id'], token)
            if instr_success:
                course_instructors[course['course_id']] = course_instrs
    
    return render_template('admin_course_manage.html',
                         admin_level=admin_level,
                         courses=courses or [],
                         instructors=instructors or [],
                         course_instructors=course_instructors)

@app.route('/admin/instructors')
def admin_instructors():
    """Instructor management page"""
    if not check_admin_role():
        return redirect(url_for('login'))
    
    token = session.get('token')
    admin_level = session.get('admin_level', 'Junior')
    
    # Fetch instructors
    success, instructors = AdminService.get_all_instructors(token)
    
    return render_template('admin_instructors.html',
                         admin_level=admin_level,
                         instructors=instructors or [])

@app.route('/admin/users')
def admin_users():
    """User management page (Senior Admin only)"""
    if not check_senior_admin():
        return redirect(url_for('login'))
    
    token = session.get('token')
    admin_level = session.get('admin_level')
    
    # Fetch all users
    success, users = AdminService.get_all_users(token)
    
    return render_template('admin_user_manage.html',
                         admin_level=admin_level,
                         users=users or [])

@app.route('/admin/moderation')
def admin_moderation():
    """Moderation page (Senior Admin only)"""
    if not check_senior_admin():
        return redirect(url_for('login'))
    
    token = session.get('token')
    admin_level = session.get('admin_level')
    
    # Mock reviews data (would need actual API for reviews)
    reviews = []
    
    return render_template('admin_moderation.html',
                         admin_level=admin_level,
                         reviews=reviews)

# ============================================================
# ADMIN API ENDPOINTS
# ============================================================

@app.route('/api/admin/assign-instructor', methods=['POST'])
def api_assign_instructor():
    """API endpoint to assign instructor"""
    if not check_admin_role():
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = session.get('token')
    data = request.get_json()
    
    success, response = AdminService.assign_instructor(data, token)
    
    if success:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route('/api/admin/remove-instructor/<int:course_id>/<int:instructor_id>', methods=['DELETE'])
def api_remove_instructor(course_id, instructor_id):
    """API endpoint to remove instructor"""
    if not check_senior_admin():
        return jsonify({'error': 'Unauthorized - Senior Admin only'}), 401
    
    token = session.get('token')
    success, response = AdminService.remove_instructor(course_id, instructor_id, token)
    
    if success:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route('/api/admin/delete-user/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    """API endpoint to delete user"""
    if not check_senior_admin():
        return jsonify({'error': 'Unauthorized - Senior Admin only'}), 401
    
    token = session.get('token')
    success, response = AdminService.delete_user(user_id, token)
    
    if success:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route('/api/admin/delete-review/<int:student_id>/<int:course_id>', methods=['DELETE'])
def api_delete_review(student_id, course_id):
    """API endpoint to delete review"""
    if not check_senior_admin():
        return jsonify({'error': 'Unauthorized - Senior Admin only'}), 401
    
    token = session.get('token')
    success, response = AdminService.delete_review(student_id, course_id, token)
    
    if success:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route('/api/admin/override-rating/<int:student_id>/<int:course_id>/<int:rating>', methods=['PUT'])
def api_override_rating(student_id, course_id, rating):
    """API endpoint to override rating"""
    if not check_senior_admin():
        return jsonify({'error': 'Unauthorized - Senior Admin only'}), 401
    
    token = session.get('token')
    success, response = AdminService.override_rating(student_id, course_id, rating, token)
    
    if success:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route('/api/admin/force-completion/<int:student_id>/<int:course_id>', methods=['PUT'])
def api_force_completion(student_id, course_id):
    """API endpoint to force mark as complete"""
    if not check_senior_admin():
        return jsonify({'error': 'Unauthorized - Senior Admin only'}), 401
    
    token = session.get('token')
    success, response = AdminService.force_completion(student_id, course_id, token)
    
    if success:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create session directory if it doesn't exist
    os.makedirs('flask_session', exist_ok=True)
    app.run(debug=True, port=5000)

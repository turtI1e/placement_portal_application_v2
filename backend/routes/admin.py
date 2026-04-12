from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from extensions import cache

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'msg': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ---------- Dashboard (cached) ----------
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def dashboard():
    print("Auth header:", request.headers.get('Authorization'))
    cache_key = 'admin_dashboard_stats'
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    from models import Student, Company, Drive, Application
    db = current_app.db
    total_students = db.session.query(Student).count()
    total_companies = db.session.query(Company).count()
    total_drives = db.session.query(Drive).count()
    total_applications = db.session.query(Application).count()
    data = {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'total_applications': total_applications
    }
    cache.set(cache_key, data, timeout=300)
    return jsonify(data), 200


# ---------- Companies (cached, search aware) ----------
@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
@admin_required
def get_companies():
    search = request.args.get('search', '').strip()
    # Create a cache key that includes the search term
    cache_key = f'admin_companies_{search}'
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    from models import Company, User
    db = current_app.db
    query = db.session.query(Company).join(User)
    if search:
        query = query.filter(
            (Company.company_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    companies = query.all()
    result = [{
        'user_id': c.user_id,
        'company_name': c.company_name,
        'email': c.user.email,
        'hr_contact': c.hr_contact,
        'approved': c.approved,
        'is_active': c.user.is_active
    } for c in companies]
    cache.set(cache_key, result, timeout=300)
    return jsonify(result), 200


# ---------- Students (cached, search aware) ----------
@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@admin_required
def get_students():
    search = request.args.get('search', '').strip()
    cache_key = f'admin_students_{search}'
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    from models import Student, User
    db = current_app.db
    query = db.session.query(Student).join(User)
    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    students = query.all()
    result = [{
        'user_id': s.user_id,
        'name': s.name,
        'email': s.user.email,
        'contact': s.contact,
        'branch': s.branch,
        'year': s.year,
        'cgpa': s.cgpa,
        'is_active': s.user.is_active
    } for s in students]
    cache.set(cache_key, result, timeout=300)
    return jsonify(result), 200


# ---------- Drives (cached) ----------
@admin_bp.route('/drives', methods=['GET'])
@jwt_required()
@admin_required
def get_drives():
    cache_key = 'admin_drives'
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    from models import Drive, Company
    db = current_app.db
    drives = db.session.query(Drive).join(Company).all()
    result = [{
        'id': d.id,
        'company_name': d.company.company_name,
        'job_title': d.job_title,
        'deadline': d.deadline.isoformat(),
        'status': d.status
    } for d in drives]
    cache.set(cache_key, result, timeout=300)
    return jsonify(result), 200


# ---------- Applications (no caching – real‑time data) ----------
@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
@admin_required
def get_all_applications():
    from models import Application
    db = current_app.db
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    pagination = db.session.query(Application).order_by(Application.application_date.desc()).paginate(page=page, per_page=per_page)
    result = [{
        'id': app.id,
        'student_name': app.student.name,
        'student_email': app.student.user.email,
        'company_name': app.drive.company.company_name,
        'job_title': app.drive.job_title,
        'applied_on': app.application_date.isoformat(),
        'status': app.status
    } for app in pagination.items]
    return jsonify({
        'applications': result,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


# ---------- Company Actions ----------
@admin_bp.route('/companies/<int:company_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_company(company_id):
    from models import Company
    db = current_app.db
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({'msg': 'Company not found'}), 404
    company.approved = True
    db.session.commit()
    # Invalidate related caches
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_companies_')
    # Also delete any search‑based company caches (optional)
    return jsonify({'msg': 'Company approved successfully'}), 200


@admin_bp.route('/companies/<int:company_id>/reject', methods=['DELETE'])
@jwt_required()
@admin_required
def reject_company(company_id):
    from models import Company, User
    db = current_app.db
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({'msg': 'Company not found'}), 404
    user = db.session.get(User, company.user_id)
    db.session.delete(company)
    if user:
        db.session.delete(user)
    db.session.commit()
    # Invalidate caches
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_companies_')
    return jsonify({'msg': 'Company rejected and deleted'}), 200


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['POST'])
@jwt_required()
@admin_required
def blacklist_company(company_id):
    from models import Company
    db = current_app.db
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({'msg': 'Company not found'}), 404
    company.user.is_active = False
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_companies_')
    return jsonify({'msg': 'Company blacklisted'}), 200


@admin_bp.route('/companies/<int:company_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_company(company_id):
    from models import Company
    db = current_app.db
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({'msg': 'Company not found'}), 404
    company.user.is_active = True
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_companies_')
    return jsonify({'msg': 'Company activated'}), 200


# ---------- Student Actions ----------
@admin_bp.route('/students/<int:student_id>/blacklist', methods=['POST'])
@jwt_required()
@admin_required
def blacklist_student(student_id):
    from models import Student
    db = current_app.db
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'msg': 'Student not found'}), 404
    student.user.is_active = False
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_students_')
    return jsonify({'msg': 'Student blacklisted'}), 200


@admin_bp.route('/students/<int:student_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_student(student_id):
    from models import Student
    db = current_app.db
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'msg': 'Student not found'}), 404
    student.user.is_active = True
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_students_')
    return jsonify({'msg': 'Student activated'}), 200


# ---------- Drive Actions ----------
@admin_bp.route('/drives/<int:drive_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_drive(drive_id):
    from models import Drive
    db = current_app.db
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    drive.status = 'approved'
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_drives')
    return jsonify({'msg': 'Drive approved'}), 200


@admin_bp.route('/drives/<int:drive_id>/reject', methods=['POST'])
@jwt_required()
@admin_required
def reject_drive(drive_id):
    from models import Drive
    db = current_app.db
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    db.session.delete(drive)
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_drives')
    return jsonify({'msg': 'Drive rejected and deleted'}), 200


@admin_bp.route('/drives/<int:drive_id>/close', methods=['POST'])
@jwt_required()
@admin_required
def close_drive(drive_id):
    from models import Drive
    db = current_app.db
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    drive.status = 'closed'
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_drives')
    return jsonify({'msg': 'Drive closed'}), 200


# ---------- Debug Endpoints ----------
@admin_bp.route('/check-token', methods=['GET'])
@jwt_required()
def check_token():
    from flask_jwt_extended import get_jwt
    return jsonify(get_jwt())


@admin_bp.route('/debug-headers', methods=['GET'])
@jwt_required(optional=True)
def debug_headers():
    from flask_jwt_extended import get_jwt_identity, get_jwt
    auth_header = request.headers.get('Authorization')
    return jsonify({
        'auth_header': auth_header,
        'jwt_identity': get_jwt_identity(),
        'jwt_claims': get_jwt(),
        'cookies': request.cookies
    }), 200

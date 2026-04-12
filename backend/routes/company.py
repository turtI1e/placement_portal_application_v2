# ================================================
# backend/routes/company.py
# COMPLETE & CLEANED VERSION (Fixed & Ready)
# ================================================

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from datetime import datetime, date

company_bp = Blueprint('company', __name__)


def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return jsonify({'msg': 'Company access required'}), 403

        user_id = get_jwt_identity()
        db = current_app.db
        from models import User, Company

        user = db.session.get(User, user_id)
        if not user or not user.is_active:
            return jsonify({'msg': 'Account is inactive or blacklisted'}), 403

        company = db.session.get(Company, user_id)
        if not company or not company.approved:
            return jsonify({'msg': 'Company not approved'}), 403

        return f(*args, **kwargs)
    return decorated_function


# ==================== DASHBOARD ====================
@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@company_required
def dashboard():
    from models import Company, Drive
    db = current_app.db
    user_id = get_jwt_identity()
    company = db.session.get(Company, user_id)
    drives = company.drives.all()

    drive_data = [{
        'id': drive.id,
        'job_title': drive.job_title,
        'deadline': drive.deadline.isoformat(),
        'status': drive.status,
        'applicants_count': drive.applications.count()
    } for drive in drives]

    return jsonify({
        'company': {
            'company_name': company.company_name,
            'hr_contact': company.hr_contact,
            'website': company.website,
            'approved': company.approved
        },
        'drives': drive_data
    }), 200


# ==================== PROFILE ====================
@company_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
@company_required
def profile():
    from models import Company
    db = current_app.db
    user_id = get_jwt_identity()
    company = db.session.get(Company, user_id)

    if request.method == 'GET':
        return jsonify({
            'company_name': company.company_name,
            'hr_contact': company.hr_contact,
            'website': company.website
        }), 200
    else:  # PUT
        data = request.get_json()
        company.company_name = data.get('company_name', company.company_name)
        company.hr_contact = data.get('hr_contact', company.hr_contact)
        company.website = data.get('website', company.website)
        db.session.commit()
        return jsonify({'msg': 'Profile updated'}), 200


# ==================== DRIVES ====================
@company_bp.route('/drives', methods=['GET'])
@jwt_required()
@company_required
def get_drives():
    from models import Company, Drive
    db = current_app.db
    user_id = get_jwt_identity()
    company = db.session.get(Company, user_id)
    drives = company.drives.all()

    result = [{
        'id': drive.id,
        'job_title': drive.job_title,
        'description': drive.description,
        'eligibility': drive.eligibility,
        'deadline': drive.deadline.isoformat(),
        'status': drive.status
    } for drive in drives]
    return jsonify(result), 200


@company_bp.route('/drives/<int:drive_id>', methods=['GET'])
@jwt_required()
@company_required
def get_drive(drive_id):
    from models import Drive
    db = current_app.db
    user_id = int(get_jwt_identity())
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    if drive.company_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    return jsonify({
        'id': drive.id,
        'job_title': drive.job_title,
        'description': drive.description,
        'eligibility': drive.eligibility,
        'deadline': drive.deadline.isoformat()
    }), 200


@company_bp.route('/drives', methods=['POST'])
@jwt_required()
@company_required
def create_drive():
    from models import Drive
    db = current_app.db
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ['job_title', 'description', 'deadline']
    if not all(k in data for k in required):
        return jsonify({'msg': 'Missing required fields'}), 400

    try:
        deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        if deadline < date.today():
            return jsonify({'msg': 'Deadline must be in the future'}), 400
    except ValueError:
        return jsonify({'msg': 'Invalid deadline format, use YYYY-MM-DD'}), 400

    drive = Drive(
        company_id=user_id,
        job_title=data['job_title'],
        description=data['description'],
        eligibility=data.get('eligibility', ''),
        deadline=deadline,
        status='pending'
    )
    db.session.add(drive)
    db.session.commit()

    from extensions import cache
    cache.delete('admin_drives')
    cache.delete('admin_dashboard_stats')

    return jsonify({'msg': 'Drive created, pending approval'}), 201


@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@jwt_required()
@company_required
def update_drive(drive_id):
    from models import Drive
    db = current_app.db
    user_id = int(get_jwt_identity())
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    if drive.company_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    # Prevent editing if already approved or closed
    if drive.status in ['approved', 'closed']:
        return jsonify({'msg': 'Cannot edit an approved or closed drive'}), 400

    data = request.get_json()
    drive.job_title = data.get('job_title', drive.job_title)
    drive.description = data.get('description', drive.description)
    drive.eligibility = data.get('eligibility', drive.eligibility)

    if 'deadline' in data:
        try:
            new_deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            if new_deadline < date.today():
                return jsonify({'msg': 'Deadline must be in the future'}), 400
            drive.deadline = new_deadline
        except ValueError:
            return jsonify({'msg': 'Invalid deadline format'}), 400

    db.session.commit()
    return jsonify({'msg': 'Drive updated'}), 200


@company_bp.route('/drives/<int:drive_id>', methods=['DELETE'])
@jwt_required()
@company_required
def delete_drive(drive_id):
    from models import Drive
    db = current_app.db
    user_id = int(get_jwt_identity())
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    if drive.company_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    if drive.status == 'approved':
        return jsonify({'msg': 'Cannot delete an approved drive'}), 400

    db.session.delete(drive)
    db.session.commit()
    return jsonify({'msg': 'Drive deleted'}), 200


@company_bp.route('/drives/<int:drive_id>/close', methods=['POST'])
@jwt_required()
@company_required
def close_drive(drive_id):
    from models import Drive
    db = current_app.db
    user_id = int(get_jwt_identity())
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    if drive.company_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    drive.status = 'closed'
    db.session.commit()
    return jsonify({'msg': 'Drive closed'}), 200


# ==================== APPLICATIONS ====================
@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
@company_required
def get_applications(drive_id):
    from models import Drive, Application
    db = current_app.db
    user_id = int(get_jwt_identity())
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    if drive.company_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    pagination = drive.applications.order_by(Application.application_date.desc()).paginate(page=page, per_page=per_page)

    result = []
    for app in pagination.items:
        student = app.student
        result.append({
            'id': app.id,
            'student_name': student.name,
            'student_email': student.user.email,
            'student_contact': student.contact,
            'student_branch': student.branch,
            'student_year': student.year,
            'student_cgpa': student.cgpa,
            'resume_path': student.resume_path,
            'application_date': app.application_date.isoformat(),
            'status': app.status,
            'drive_title': drive.job_title
        })

    return jsonify({
        'applications': result,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@company_bp.route('/applications/<int:app_id>', methods=['PUT'])
@jwt_required()
@company_required
def update_application_status(app_id):
    from models import Application
    db = current_app.db
    user_id = int(get_jwt_identity())
    app = db.session.get(Application, app_id)
    if not app:
        return jsonify({'msg': 'Application not found'}), 404

    drive = app.drive
    if drive.company_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    data = request.get_json()
    new_status = data.get('status')
    allowed = ['applied', 'shortlisted', 'selected', 'rejected']
    if new_status not in allowed:
        return jsonify({'msg': 'Invalid status'}), 400

    app.status = new_status
    db.session.commit()
    return jsonify({'msg': 'Application status updated'}), 200

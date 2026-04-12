from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
import os
from werkzeug.utils import secure_filename
from celery_app import celery
from tasks.export_csv import export_applications_csv
from celery.result import AsyncResult

student_bp = Blueprint('student', __name__)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'student':
            return jsonify({'msg': 'Student access required'}), 403

        user_id = get_jwt_identity()
        db = current_app.db
        from models import User

        user = db.session.get(User, user_id)
        if not user or not user.is_active:
            return jsonify({'msg': 'Account is inactive'}), 403

        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

def parse_eligibility(eligibility_str):
    """Parse eligibility string like 'branch:CS,IT; min_cgpa:7.0; year:3,4'"""
    criteria = {}
    if not eligibility_str:
        return criteria
    parts = [p.strip() for p in eligibility_str.split(';') if p.strip()]
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key == 'branch':
                criteria['branches'] = [b.strip().lower() for b in value.split(',')]
            elif key == 'min_cgpa':
                try:
                    criteria['min_cgpa'] = float(value)
                except ValueError:
                    pass
            elif key == 'year':
                criteria['years'] = [int(y.strip()) for y in value.split(',') if y.strip().isdigit()]
    return criteria

def check_eligibility(student, drive):
    """Return (is_eligible, reason)"""
    criteria = parse_eligibility(drive.eligibility)
    if not criteria:
        return True, ""
    if 'branches' in criteria and student.branch:
        if student.branch.lower() not in criteria['branches']:
            return False, f"Branch {student.branch} not allowed"
    if 'min_cgpa' in criteria and student.cgpa is not None:
        if student.cgpa < criteria['min_cgpa']:
            return False, f"CGPA {student.cgpa} below minimum {criteria['min_cgpa']}"
    if 'years' in criteria and student.year is not None:
        if student.year not in criteria['years']:
            return False, f"Year {student.year} not allowed"
    return True, ""

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@student_required
def dashboard():
    from models import Student, Drive, Application
    db = current_app.db
    user_id = get_jwt_identity()
    student = db.session.query(Student).get(user_id)
    drives = db.session.query(Drive).filter_by(status='approved').all()
    applied_drives = student.applications.all()
    return jsonify({
        'student': {
            'name': student.name,
            'email': student.user.email,
            'contact': student.contact,
            'branch': student.branch,
            'year': student.year,
            'cgpa': student.cgpa,
            'resume_path': student.resume_path
        },
        'approved_drives_count': len(drives),
        'applied_drives_count': len(applied_drives)
    }), 200

@student_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
@student_required
def profile():
    from models import Student
    db = current_app.db
    user_id = get_jwt_identity()
    student = db.session.query(Student).get(user_id)
    if request.method == 'GET':
        return jsonify({
            'name': student.name,
            'contact': student.contact,
            'branch': student.branch,
            'year': student.year,
            'cgpa': student.cgpa,
            'resume_path': student.resume_path
        }), 200
    else:  # PUT
        data = request.get_json()
        student.name = data.get('name', student.name)
        student.contact = data.get('contact', student.contact)
        student.branch = data.get('branch', student.branch)
        student.year = data.get('year', student.year)
        student.cgpa = data.get('cgpa', student.cgpa)
        db.session.commit()
        return jsonify({'msg': 'Profile updated'}), 200

@student_bp.route('/resume', methods=['POST'])
@jwt_required()
@student_required
def upload_resume():
    from models import Student
    db = current_app.db
    user_id = get_jwt_identity()
    student = db.session.query(Student).get(user_id)
    if 'resume' not in request.files:
        return jsonify({'msg': 'No file part'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"student_{user_id}_{file.filename}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        student.resume_path = filename
        db.session.commit()
        return jsonify({'msg': 'Resume uploaded', 'resume_path': filename}), 200
    return jsonify({'msg': 'File type not allowed'}), 400

@student_bp.route('/drives', methods=['GET'])
@jwt_required()
@student_required
def get_drives():
    from models import Drive, Application, Company
    from datetime import date
    db = current_app.db
    search = request.args.get('search', '')
    user_id = get_jwt_identity()
    query = db.session.query(Drive).filter(Drive.status == 'approved', Drive.deadline >= date.today())
    if search:
        query = query.filter(
            (Drive.job_title.contains(search)) |
            (Drive.eligibility.contains(search)) |
            (Drive.company.has(Company.company_name.contains(search)))
        )
    drives = query.all()
    result = []
    for d in drives:
        applied = db.session.query(Application).filter_by(student_id=user_id, drive_id=d.id).first() is not None
        result.append({
            'id': d.id,
            'company_name': d.company.company_name,
            'job_title': d.job_title,
            'description': d.description,
            'eligibility': d.eligibility,
            'deadline': d.deadline.isoformat(),
            'applied': applied
        })
    return jsonify(result), 200

@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@jwt_required()
@student_required
def apply_drive(drive_id):
    from models import Drive, Student, Application
    from datetime import date
    db = current_app.db
    user_id = get_jwt_identity()
    drive = db.session.query(Drive).get(drive_id)
    if not drive:
        return jsonify({'msg': 'Drive not found'}), 404
    if drive.status != 'approved':
        return jsonify({'msg': 'Drive is not open for applications'}), 400
    if drive.deadline < date.today():
        return jsonify({'msg': 'Application deadline has passed'}), 400

    student = db.session.query(Student).get(user_id)
    eligible, reason = check_eligibility(student, drive)
    if not eligible:
        return jsonify({'msg': f'Not eligible: {reason}'}), 400

    if not student.user.is_active:
        return jsonify({'msg': 'Account is inactive'}), 403

    existing = db.session.query(Application).filter_by(student_id=user_id, drive_id=drive_id).first()
    if existing:
        return jsonify({'msg': 'Already applied'}), 400

    app = Application(student_id=user_id, drive_id=drive_id, status='applied')
    db.session.add(app)
    db.session.commit()
    return jsonify({'msg': 'Application submitted'}), 201

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
@student_required
def get_applications():
    from models import Application
    db = current_app.db
    user_id = get_jwt_identity()
    applications = db.session.query(Application).filter_by(student_id=user_id).all()
    result = []
    for app in applications:
        result.append({
            'id': app.id,
            'drive_id': app.drive_id,
            'company_name': app.drive.company.company_name,
            'job_title': app.drive.job_title,
            'applied_on': app.application_date.isoformat(),
            'status': app.status
        })
    return jsonify(result), 200

@student_bp.route('/export/applications', methods=['POST'])
@jwt_required()
@student_required
def trigger_export():
    user_id = get_jwt_identity()
    task = export_applications_csv.delay(user_id)
    return jsonify({'task_id': task.id}), 202

@student_bp.route('/export/status/<task_id>', methods=['GET'])
@jwt_required()
@student_required
def export_status(task_id):
    task = AsyncResult(task_id, app=celery)
    if task.ready():
        result = task.result
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'status': 'FAILURE', 'error': result['error']}), 500
        return jsonify({'status': 'SUCCESS', 'result': result}), 200
    else:
        return jsonify({'status': task.state}), 200

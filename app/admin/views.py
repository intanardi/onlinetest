import datetime
from datetime import datetime, date, time, timedelta
from flask import render_template, session, redirect, url_for, flash, request, current_app, Flask, send_from_directory, send_file
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from . import admin
from .. import db, csrf
from ..models import *
from ..utils import convert_in_hours, convert_in_minutes, duration_format_allowed
import json
import random
import os
from os.path import join, dirname, realpath
import re
import io
from zipfile import ZipFile

apps = Flask(__name__)
apps.config['UPLOAD_PATH'] = 'app/static/uploads/test'

# UPLOADS_TEST_PATH = join(dirname(realpath(__file__)), 'static/upload/')

ROWS_PER_PAGE = 10
ADMIN_PERMISSION_LIST = [1,2]
UPLOAD_FOLDER = '/static/upload'
ALLOWED_EXTENSIONS = {'pdf'}
title = "Feniks CBT"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/open/pdf/test/<filename>')
@login_required
def open_pdf(filename):
    directory = "/static/uploads/test/" + filename
    print(directory)
    return render_template('pdf_dashboard/preview.html', directory=directory)

@admin.route('/open/pdf/result/<filename>')
@login_required
def open_result_pdf(filename):
    # directory = "/static/pdf/psikotest/soal_cfit.pdf"
    directory = "/static/uploads/result/" + filename
    print(directory)
    return render_template('pdf_dashboard/preview.html', directory=directory)

@admin.route('/open/pdf/result/download/<path:filename>', methods=['GET', 'POST'])
@login_required
def download_result(filename):
    print("hyeyeyeyeyeyeyeree")
    print("----")
    print(filename)
    directory = 'static/uploads/result/' + filename
    return send_file(directory, as_attachment=True)

@admin.route('/')
@admin.route('/index')
@csrf.exempt
@login_required
def index():
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    current_date = date.today()
    active_admin = User.query.filter(User.role_id.in_(ADMIN_PERMISSION_LIST),User.is_deleted.is_(False)).count()
    inactive_admin = User.query.filter(User.role_id.in_(ADMIN_PERMISSION_LIST),User.is_deleted.is_(True)).count()
    total_candidate = User.query.filter_by(role_id=3,is_deleted=False).count()
    new_candidate = User.query.filter_by(added_time=current_date).count()
    return render_template('admin/index.html', inactive_admin=inactive_admin, active_admin=active_admin, total_candidate=total_candidate, new_candidate=new_candidate)
"""
    =================================================
                    USER ADMIN MODULE
    =================================================
"""

@admin.route('/data', methods=['POST', 'GET'])
@csrf.exempt
@login_required
def data():
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    _search = "%{}%".format(_keyword)
    start = 0
    if page > 1:
        start = page * ROWS_PER_PAGE - ROWS_PER_PAGE
    total_rows = User.query.filter(User.role_id.in_(ADMIN_PERMISSION_LIST),User.fullname.like(_search) ,User.is_deleted.is_(False)).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // -boxsize)
    users = User.query.filter(User.role_id.in_(ADMIN_PERMISSION_LIST),User.fullname.like(_search) ,User.is_deleted.is_(False)).order_by(User.id).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.data', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('admin.data', page=users.prev_num) \
        if users.has_prev else None
    return render_template('admin/admin/index.html', users=users.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages), title=title, start=start)

@admin.route('/add', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def add():
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('admin.index'))
    roles = Role.query.all()
    divisions = Division.query.all()
    levels = Level.query.all()
    if request.method == 'POST':
        check_existing = User.query.all()
        for c in check_existing:
            if request.form['username'].lower() == c.username:
                flash("username is already exist. please use another one")
                return redirect(url_for('admin.add'))
            if request.form['email'].lower() == c.email:
                flash("email is already registered!")
                return redirect(url_for('admin.add'))
            if request.form['phone'].lower() == c.phone:
                flash("phone is already registered!")
                return redirect(url_for('admin.add'))

        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", request.form['email'] ):
            flash("Please fill the email format correctly")
            return redirect(url_for('admin.add'))
        user = User()
        user.role_id = int(request.form['roles'])
        user.division_id = int(request.form['division'])
        user.level_id = int(request.form['level'])
        user.username = request.form['username']
        user.phone = request.form['phone']
        user.email = request.form['email']
        user.fullname = request.form['fullname']
        user.address = request.form['address']
        user.added_time = date.today()
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.data'))
        
    return render_template('admin/admin/add.html', roles=roles, divisions=divisions, levels=levels)

@admin.route('/global_setting/data', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def data_global_setting():
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    
    global_setting = Global_Setting.query.all()
        
    return render_template('admin/global_setting/index.html', global_setting=global_setting, title=title)

@admin.route('/global_setting/add', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def add_global_setting():
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == 'POST':
        gs = Global_Setting()
        gs.name = request.form['name']
        gs.setting_code = request.form['setting_code']
        gs.variable = request.form['variable']
        db.session.add(gs)
        db.session.commit()
        return redirect(url_for('admin.data'))
        
    return render_template('admin/global_setting/add.html', title=title)

@admin.route('/global_setting/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def edit_global_setting(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    global_setting = Global_Setting.query.filter_by(id=id).first()
    if request.method == 'POST':
        global_setting.name = request.form['name']
        global_setting.setting_code = request.form['setting_code']
        global_setting.variable = request.form['variable']
        db.session.add(global_setting)
        db.session.commit()
        return redirect(url_for('admin.data_global_setting'))
        
    return render_template('admin/global_setting/edit.html', global_setting=global_setting, title=title)

@admin.route('/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def edit(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('admin.index'))
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    divisions = Division.query.all()
    levels = Level.query.all()
    # check_user = User.query.filter(User.id != id, User.is_deleted.is_(False)).all()
    # print(check_user[1])
    # if "Ramzavealouve".lower() in check_user.lower():
    #     print("found")
    # return True
    if request.method == 'POST':
        if  'roles' in request.form:
            user.role_id = int(request.form['roles'])
        if  'division' in request.form:
            user.division_id = int(request.form['division'])
        if  'level' in request.form:
            user.level_id = int(request.form['level'])
        check_user = User.query.filter(User.id != id, User.is_deleted.is_(False)).all()
        for c in check_user:
            if request.form['email'].lower() == c.email:
                flash("Email sudah ada!")
                return redirect(url_for('admin.edit', id=id))
            if request.form['username'].lower() == c.username:
                flash("Username sudah ada!")
                return redirect(url_for('admin.edit', id=id))
            if request.form['phone'].lower() == c.phone:
                flash("Phone sudah ada!")
                return redirect(url_for('admin.edit', id=id))
        user.username = request.form['username']
        user.email = request.form['email']  
        user.fullname = request.form['fullname']
        user.phone = request.form['phone'] 
        user.address = request.form['address'] 
        # user.role_id = int(request.form['roles'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.data'))
    return render_template('admin/admin/edit.html', user=user, roles=roles, divisions=divisions, levels=levels)

@admin.route('/view/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def view(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    
    user = User.query.filter_by(id=id).first()
    username = user.username
    if current_user.role_id != 1:
        if int(current_user.id) != int(id):
            username = "*****"
    roles = Role.query.all()
    divisions = Division.query.all()
    levels = Level.query.all()
    return render_template('admin/admin/view.html', user=user, roles=roles, divisions=divisions, levels=levels, title=title, username=username)

@admin.route('/admin_set_password/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def admin_set_password(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('admin.index'))
    user = User.query.filter_by(id=id).first()
    if request.method == "POST":
        if request.form['password'] != request.form['repassword'] :
            flash("You type different password confirmation!")
            return redirect(url_for('admin.admin_set_password', id=id))
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.data'))
    return render_template('admin/admin/set_password.html', user=user, title=title)

@admin.route('/update_profile/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def update_profile(id):
    user = User.query.filter_by(id=id).first()
    if int(current_user.id) != int(id):
        flash("Page Error")
        return redirect(url_for("admin.index"))
    if request.method == "POST":
        if  'roles' in request.form:
            user.role_id = int(request.form['roles'])
        if  'division' in request.form:
            user.division_id = int(request.form['division'])
        if  'level' in request.form:
            user.level_id = int(request.form['level'])
        check_user = User.query.filter(User.id != id, User.is_deleted.is_(False)).all()
        for c in check_user:
            if request.form['email'].lower() == c.email:
                flash("Email sudah ada!")
                return redirect(url_for('admin.edit', id=id))
            if request.form['phone'].lower() == c.phone:
                flash("Phone sudah ada!")
                return redirect(url_for('admin.edit', id=id))
        user.email = request.form['email']  
        user.fullname = request.form['fullname']
        user.phone = request.form['phone'] 
        user.address = request.form['address'] 
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.data'))
    return render_template('admin/admin/update_profile.html', user=user, title=title)

@admin.route('/admin_change_password/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def admin_change_password(id):
    user = User.query.filter_by(id=id).first()
    if int(current_user.id) != int(id):
        flash("Page Error")
        return redirect(url_for("admin.index"))
    if request.method == "POST":
        if request.form['password'] != request.form['repassword'] :
            flash("You type a different password confirmation!")
            return redirect(url_for('admin.admin_change_password', id=id))
        if user.check_password(request.form['oldpassword']) == False:
            flash("Old password is wrong!")
            return redirect(url_for('admin.admin_change_password', id=id))
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.data'))
    return render_template('admin/admin/admin_change_password.html', user=user, title=title)

@admin.route('/delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def delete(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('user.index'))
    user = User.query.filter_by(id=id).first()
    user.is_deleted = True
    db.session.add(user)
    # db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.data'))

"""
    =====================================================
                    END OF USER ADMIN MODULE
    =====================================================
"""

"""
    =====================================================
                    USER CANDIDATE MODULE
    =====================================================
"""


@admin.route('/candidate/data', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def candidate_data():
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    start = 0
    if page > 1:
        start = page * ROWS_PER_PAGE - ROWS_PER_PAGE
    _search = "%{}%".format(_keyword)
    total_rows = User.query.filter(User.role_id.in_(["3"]), User.is_deleted.is_(False), User.fullname.like(_search)).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // -boxsize)
    candidates = db.session.query(User.id, User.fullname.label('name'), User.email, User.phone, Level.name.label('level'), Division.name.label('division'), Candidate_Test_Schedule.date_test.label('schedule')).join(Level, Division, Candidate_Test_Schedule, isouter=True).filter(User.role_id.in_(["3"]), User.is_deleted.is_(False), User.fullname.like(_search)).order_by(User.id).paginate(page=page, per_page=ROWS_PER_PAGE)
    # print(candidates.items)
    # candidates = User.query.filter(User.role_id.in_(["3"]), User.is_deleted.is_(False), User.fullname.like(_search)).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.candidate_data', page=candidates.next_num) \
        if candidates.has_next else None
    prev_url = url_for('admin.candidate_data', page=candidates.prev_num) \
        if candidates.has_prev else None
    return render_template('admin/candidate/index.html', candidates=candidates.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages), title=title, start=start)
    
@login_required
@admin.route('/candidate/add', methods=['GET', 'POST'])
@csrf.exempt
def candidate_add():
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    divisions = Division.query.all()
    levels = Level.query.all()
    # print(time)
    # return "njay"
    if request.method == 'POST':
        print(request.form)
        check_existing = User.query.all()
        for c in check_existing:
            if request.form['username'].lower() == c.username:
                flash("username is already exist. please use another one")
                return redirect(url_for('admin.candidate_add'))
            if request.form['email'].lower() == c.email:
                flash("email already registered!")
                return redirect(url_for('admin.candidate_add'))
            if request.form['phone'].lower() == c.phone:
                flash("phone already registered!")
                return redirect(url_for('admin.candidate_add'))
        candidate = User()
        candidate.username = request.form['username'] 
        candidate.email = request.form['email']  
        candidate.fullname = request.form['fullname']
        candidate.phone = request.form['phone'] 
        candidate.address = request.form['address'] 
        candidate.division_id = request.form['division'] 
        candidate.level_id = request.form['level']
        candidate.set_password(request.form['password'])
        db.session.add(candidate)
        db.session.commit()
        return redirect(url_for('admin.candidate_data'))
        
    return render_template('admin/candidate/add.html', divisions=divisions, levels=levels,title=title)

@admin.route('/candidate/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def candidate_edit(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    divisions = Division.query.all()
    levels = Level.query.all()
    candidate = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        check_user = User.query.filter(User.id != id, User.is_deleted.is_(False)).all()
        for c in check_user:
            if request.form['email'].lower() == c.email:
                flash("Email sudah ada!")
                return redirect(url_for('admin.edit', id=id))
            if request.form['username'].lower() == c.username:
                flash("Username sudah ada!")
                return redirect(url_for('admin.edit', id=id))
            if request.form['phone'].lower() == c.phone:
                flash("Phone sudah ada!")
                return redirect(url_for('admin.edit', id=id))
        candidate.username = request.form['username']
        candidate.email = request.form['email']  
        candidate.fullname = request.form['fullname']
        candidate.phone = request.form['phone'] 
        candidate.address = request.form['address']
        candidate.division_id = request.form['division'] 
        candidate.level_id = request.form['level']
        db.session.add(candidate)
        db.session.commit()
        return redirect(url_for('admin.candidate_data'))
    return render_template('admin/candidate/edit.html', candidate=candidate, divisions=divisions, levels=levels,title=title)

@admin.route('/candidate/view/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def candidate_view(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    candidate = User.query.filter_by(id=id).first()
    return render_template('admin/candidate/view.html', candidate=candidate, title=title)

@admin.route('/candidate/set_schedule/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def candidate_set_schedule(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    schedule_date = ""
    schedule_time = ""
    schedule = Candidate_Test_Schedule()
    divisions = Division.query.all()
    levels = Level.query.all()
    candidate = User.query.filter_by(id=id).first()
    is_time_set = Candidate_Test_Schedule.query.filter_by(candidate_id=candidate.id).first()
    if is_time_set:
        schedule_date = is_time_set.date_test.strftime("%m/%d/%Y")
        schedule_time = is_time_set.date_test.strftime("%H:%M")
        schedule = is_time_set
    # print(schedule)
    if request.method == 'POST':
        timeFormated = request.form['date']+" "+request.form['time']
        datetimeformated = datetime.strptime(timeFormated,'%m/%d/%Y %H:%M')
        schedule.candidate_id = id
        schedule.date_test = datetimeformated
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('admin.candidate_data'))
    return render_template('admin/candidate/set_schedule_add.html', candidate=candidate, schedule_date=schedule_date, schedule_time=schedule_time,title=title)

@admin.route('/candidate_set_password/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def candidate_set_password(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('admin.index'))
    user = User.query.filter_by(id=id).first()
    if request.method == "POST":
        if request.form['password'] != request.form['repassword'] :
            flash("You type different password confirmation!")
            return redirect(url_for('admin.admin_set_password', id=id))
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.candidate_data'))
    return render_template('admin/candidate/set_password.html', user=user, title=title)

@admin.route('/candidate/delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def candidate_delete(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    cst = Candidate_Test_Schedule.query.filter_by(candidate_id=id).delete()
    cms = Candidate_Main_Schedule.query.filter_by(candidate_id=id).delete()
    cps = Candidate_Psikotest_Schedule.query.filter_by(candidate_id=id).delete()
    candidate = User.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('admin.candidate_data'))

"""
    =====================================================
                    END OF CANDIDATE MODULE
    =====================================================
"""

"""
    =====================================================
                    EXAMINATION MODULE
    =====================================================
"""

@admin.route('/examination/data', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def examination_data():
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    start = 0
    if page >0 :
        start = page * ROWS_PER_PAGE -ROWS_PER_PAGE
    _search = "%{}%".format(_keyword)
    total_rows = Examination.query.filter(Examination.is_deleted.is_(False)).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // -boxsize)
    examination = Examination.query.filter(Examination.name.like(_search), Examination.is_deleted.is_(False)).order_by('name').paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.examination_data', page=examination.next_num) \
        if examination.has_next else None
    prev_url = url_for('admin.examination_data', page=examination.prev_num) \
        if examination.has_prev else None
    return render_template('admin/examination/index.html', examinations=examination.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages),title=title, start=start)


@admin.route('/examination/add', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def examination_add():
    # Check If user role is superadmin or admin
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    
    # get all data from database
    divisions = Division.query.all()
    levels = Level.query.all()
    if request.method == 'POST':
        check_availibility = Examination.query.filter_by(division_id=request.form['division'], level_id=request.form['level']).first()
        if check_availibility is not None:
            flash("The data with this setting has been already exist")
            return redirect(url_for('admin.examination_add'))
        examination = Examination()
        examination.name = request.form['name']
        examination.division_id = request.form['division']  
        examination.level_id = request.form['level']
        db.session.add(examination)
        db.session.commit()
        return redirect(url_for('admin.examination_data'))
        
    return render_template('admin/examination/add.html', levels=levels, divisions=divisions,title=title)

@admin.route('/examination/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def examination_edit(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    examination = Examination.query.filter_by(id=id).first()
    if request.method == 'POST':
        examination.name = request.form['name']
        db.session.add(examination)
        db.session.commit()
        return redirect(url_for('admin.examination_data'))
    return render_template('admin/examination/edit.html', examination=examination, title=title)

@admin.route('/examination/delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def examination_delete(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    examination = Examination.query.filter_by(id=id).first()
    db.session.delete(examination)
    db.session.commit()
    return redirect(url_for('admin.examination_data'))
"""
    =====================================================
                    END OF EXAMINATION MODULE
    =====================================================
"""

"""
    =====================================================
                    PSIKOTEST MODULE
    =====================================================
"""
@admin.route('/psikotest_type/data', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_type_data():
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    start = 0
    if page >0 :
        start = page * ROWS_PER_PAGE -ROWS_PER_PAGE
    _search = "%{}%".format(_keyword)
    total_rows = Psikotest_Type.query.filter(Psikotest_Type.is_deleted.is_(False)).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // -boxsize)
    psikotest = Psikotest_Type.query.filter(Psikotest_Type.is_deleted.is_(False)).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.psikotest_data', page=psikotest.next_num) \
        if psikotest.has_next else None
    prev_url = url_for('admin.psikotest_data', page=psikotest.prev_num) \
        if psikotest.has_prev else None
    return render_template('admin/psikotest_type/index.html', psikotests=psikotest.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages),title=title, start=start)

@admin.route('/psikotest_type/add', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_type_add():
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == 'POST':
        psikotest = Psikotest_Type()
        psikotest.name = request.form['name']
        psikotest.preliminary = request.form['preliminary']
        db.session.add(psikotest)
        db.session.commit()
        return redirect(url_for('admin.psikotest_type_data'))
        
    return render_template('admin/psikotest_type/add.html',title=title)

@admin.route('/psikotest_type/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_type_edit(id):
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    psikotest = Psikotest_Type.query.filter_by(id=id).first()
    if request.method == 'POST':
        psikotest.name = request.form['name']
        psikotest.preliminary = request.form['preliminary']
        db.session.add(psikotest)
        db.session.commit()
        return redirect(url_for('admin.psikotest_type_data'))
        
    return render_template('admin/psikotest_type/edit.html', psikotest=psikotest,title=title)

@admin.route('/psikotest_type/delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_type_delete(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    psikotest_type = Psikotest_Type.query.filter_by(id=id).first()
    psikotest = Psikotest.query.filter_by(psikotest_type_id=id).all()
    if psikotest is not None:
        for i in psikotest:
            os.remove(os.path.join(apps.config['UPLOAD_PATH'], i.test_filename))
            os.remove(os.path.join(apps.config['UPLOAD_PATH'], i.instruction_filename))
            i.is_deleted = True
            db.session.add(i)
            db.session.commit()
    psikotest_type.is_deleted = True
    db.session.add(psikotest_type)
    db.session.commit()
    return redirect(url_for('admin.psikotest_type_data'))

@admin.route('/psikotest/psikotest_data/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_data(id):
    print(id)
    print("---------------")
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    _search = "%{}%".format(_keyword)
    start = 0
    if page > 1:
        start = page * ROWS_PER_PAGE - ROWS_PER_PAGE
    psikotest_type = Psikotest_Type.query.filter_by(id=id).first()
    total_rows = Psikotest.query.filter_by(psikotest_type_id=psikotest_type.id, is_deleted=False).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // -boxsize)
    psikotests = Psikotest.query.filter_by(psikotest_type_id=psikotest_type.id, is_deleted=False).order_by(Psikotest.id).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.data', page=psikotests.next_num) \
        if psikotests.has_next else None
    prev_url = url_for('admin.data', page=psikotests.prev_num) \
        if psikotests.has_prev else None
    return render_template('admin/psikotest/index.html', psikotests=psikotests.items, psikotest_type=psikotest_type, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages), title=title, start=start)
    # Check If user role is superadmin or admin

@admin.route('/psikotest/psikotest_data/add/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_add(id):
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    psikotest_type = Psikotest_Type.query.filter_by(id=id).first()
    if request.method == 'POST':
        if request.form['minutes'] == "" or request.form['minutes'] is None:
            flash("Duration cannot be empty")
            return redirect(url_for('admin.psikotest_add', id=id))
        duration_form = request.form['minutes'].replace(",", ".")
        check_format = duration_format_allowed(duration_form)
        if check_format is False :
            flash("Duration should be in numeric or decimal")
            return redirect(url_for('admin.psikotest_add', id=id))
        duration = str(timedelta(minutes=float(duration_form)))
        instruction_file = request.files['instruction_file']
        test_file = request.files['test_file']
        if instruction_file.filename == '' or test_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        user = User.query.filter_by(id=current_user.id).first()
        random_number = random.randint(1, 100000)
        timenow = str(datetime.now())
        mytime = timenow.split('.')
        filename_instruction = str(mytime[1])+ '_'+ str(user.id)+ '_' + str(user.level_id)+ '_' + str(user.division_id)+ '_' + str(random_number) + '_'+ 'instruction.pdf'

        filename_test = str(mytime[1])+ '_'+ str(user.id)+ '_' + str(user.level_id)+ '_' + str(user.division_id)+ '_' + str(random_number) + '_'+ 'test.pdf'
        instruction_file.save(os.path.join(apps.config['UPLOAD_PATH'],filename_instruction))
        test_file.save(os.path.join(apps.config['UPLOAD_PATH'],filename_test))

        psikotest = Psikotest()
        if request.form["alert"] is not None :
            psikotest.alert = request.form['alert']
        psikotest.psikotest_type_id = id
        psikotest.test_filename = filename_instruction
        psikotest.instruction_filename = filename_test
        psikotest.duration = duration
        psikotest.timedelta_duration = duration_form
        db.session.add(psikotest)
        db.session.commit()
        return redirect(url_for('admin.psikotest_data', id=id))
        
    return render_template('admin/psikotest/add.html',title=title, psikotest_type=psikotest_type)

@admin.route('/psikotest/psikotest_data/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_edit(id):
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    psikotest = Psikotest.query.filter_by(id=id).first()
    psikotest_type = Psikotest_Type.query.filter_by(id=psikotest.psikotest_type_id).first()
    minutes = convert_in_minutes(str(psikotest.duration))
    if request.method == 'POST':
        if request.form['minutes'] == "" or request.form['minutes'] is None:
            flash("Duration cannot be empty")
            return redirect(url_for('admin.psikotest_edit', id=id))
        duration_form = request.form['minutes'].replace(",", ".")
        check_format = duration_format_allowed(duration_form)
        if check_format is False :
            flash("Duration should be in numeric or decimal")
            return redirect(url_for('admin.psikotest_edit', id=id))
        duration = str(timedelta(minutes=float(duration_form)))
        instruction_file = request.files['instruction_file']
        test_file = request.files['test_file']
        if instruction_file.filename != '' or test_file.filename != '':
            user = User.query.filter_by(id=current_user.id).first()
            random_number = random.randint(1, 100000)
            timenow = str(datetime.now())
            mytime = timenow.split('.')
            if psikotest.test_filename is not None:
                os.remove(os.path.join(apps.config['UPLOAD_PATH'], psikotest.test_filename))
            if psikotest.instruction_filename is not None:
                os.remove(os.path.join(apps.config['UPLOAD_PATH'], psikotest.instruction_filename))
            filename_instruction = str(mytime[1])+ '_'+ str(user.id)+ '_' + str(user.level_id)+ '_' + str(user.division_id)+ '_' + str(random_number) + '_'+ 'instruction.pdf'

            filename_test = str(mytime[1])+ '_'+ str(user.id)+ '_' + str(user.level_id)+ '_' + str(user.division_id)+ '_' + str(random_number) + '_'+ 'test.pdf'
            instruction_file.save(os.path.join(apps.config['UPLOAD_PATH'],filename_instruction))
            test_file.save(os.path.join(apps.config['UPLOAD_PATH'],filename_test))
            psikotest.test_filename = filename_test
            psikotest.instruction_filename = filename_instruction
        if request.form["alert"] is not None :
            psikotest.alert = request.form['alert']
        psikotest.duration = duration
        psikotest.timedelta_duration = duration_form
        db.session.add(psikotest)
        db.session.commit()
        return redirect(url_for('admin.psikotest_data', id=psikotest_type.id))
        
    return render_template('admin/psikotest/edit.html',title=title, psikotest_type=psikotest_type, psikotest=psikotest, minutes=int(minutes))

@admin.route('/psikotest/psikotest_data/delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def psikotest_delete(id):
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    psikotest = Psikotest.query.filter_by(id=id).first()
    psikotest_type = Psikotest_Type.query.filter_by(id=psikotest.psikotest_type_id).first()
    os.remove(os.path.join(apps.config['UPLOAD_PATH'], psikotest.instruction_filename))
    os.remove(os.path.join(apps.config['UPLOAD_PATH'], psikotest.test_filename))
    psikotest.is_deleted = True
    db.session.add(psikotest)
    db.session.commit()
    return redirect(url_for('admin.psikotest_data', id=psikotest_type.id))

"""
    =====================================================
                    END OF PSIKOTEST MODULE
    =====================================================
"""

"""
    =====================================================
                    QUESTION MODULE (V2)
    =====================================================
"""

@admin.route('/question/question_data/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def question_data(id):
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    start = 0
    if page > 0 :
        start = page * ROWS_PER_PAGE -ROWS_PER_PAGE
    _search = "%{}%".format(_keyword)
    get_exam = Examination.query.filter_by(id=id).first()
    division = Division.query.filter_by(id=get_exam.division_id).first()
    level = Level.query.filter_by(id=get_exam.level_id).first()
    page = request.args.get('page', 1, type=int)
    total_rows = Question.query.filter_by(examination_id=id).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // -boxsize)
    question = Question.query.filter_by(examination_id=id).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.question_data', page=question.next_num) \
        if question.has_next else None
    prev_url = url_for('admin.question_data', page=question.prev_num) \
        if question.has_prev else None
    return render_template('admin/question/index.html', quetions=question.items, level=level, division=division, get_exam=get_exam, exam_name=get_exam.name, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages),title=title, start=start)
    
@admin.route('/question/question_add/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def question_add(id):
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    
    # get all data from database
    print(id)
    get_exam = Examination.query.filter_by(id=id).first()
    division = Division.query.filter_by(id=get_exam.division_id).first()
    level = Level.query.filter_by(id=get_exam.level_id).first()
    if request.method == 'POST':
        # set variable to false
        is_multiple = False
        # check if form post got an answer list choice
        check_multiple_choices = request.form.getlist('answer[]')
        if check_multiple_choices:
            # if have a list set variable to true
            is_multiple = True
        question = Question()
        question.name = request.form['name']
        question.question_division_id = request.form['division']  
        question.question_level_id = request.form['level']
        question.question = request.form['question']
        question.is_multiple_choice = is_multiple
        db.session.add(question)
        db.session.commit()
        if is_multiple:
            for i in check_multiple_choices:
                mc = Multiple_Choice()
                mc.name = i
                mc.question_id = question.id
                db.session.add(mc)
                db.session.commit()
        # return "halo"
        return redirect(url_for('admin.question_data'))
        
    return render_template('admin/question/add.html', level=level, division=division, examination_id=id, exam_name=get_exam.name,title=title)


@admin.route('/question/question_edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def question_edit(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    question = Question.query.filter_by(id=id).first()
    get_exam = Examination.query.filter_by(id=id).first()
    division = Division.query.filter_by(id=get_exam.division_id).first()
    level = Level.query.filter_by(id=get_exam.level_id).first()
    if request.method == 'POST':
        question.username = request.form['username']
        question.email = request.form['email']  
        question.fullname = request.form['fullname']
        question.phone = request.form['phone'] 
        question.address = request.form['address']
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('admin.question_data'))
    return render_template('admin/examination_pdf/edit.html', level=level, division=division, question=question,title=title)

@admin.route('/question/question_delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def question_delete(id):
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    question = User.query.filter_by(id=id).first()
    question.is_deleted = True
    db.session.add(question)
    db.session.commit()
    return redirect(url_for('admin.question_data'))

"""
    =====================================================
                    END OF QUESTION MODULE
    =====================================================
"""

"""
    ====================================
            STATIC ONLINE IN PDF
    ====================================
"""

@admin.route('/question/question_pdf_data/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def question_pdf_data(id):
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    start = 0
    if page > 0:
        start = page * ROWS_PER_PAGE - ROWS_PER_PAGE
    _search = "%{}%".format(_keyword)
    directory = "/static/uploads/test/"
    get_exam = Examination.query.filter_by(id=id).first()
    division = Division.query.filter_by(id=get_exam.division_id).first()
    level = Level.query.filter_by(id=get_exam.level_id).first()
    page = request.args.get('page', 1, type=int)
    total_rows = Examination_Detail.query.filter_by(examination_id=id, is_deleted=False).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // - boxsize)
    question_pdf = Examination_Detail.query.filter_by(examination_id=id, is_deleted=False).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.question_data', page=question_pdf.next_num) \
        if question_pdf.has_next else None
    prev_url = url_for('admin.question_data', page=question_pdf.prev_num) \
        if question_pdf.has_prev else None
    return render_template('admin/examination_pdf/index.html', quetions=question_pdf.items, level=level, division=division, get_exam=get_exam, exam_name=get_exam.name, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages), directory=directory, start=start)

@admin.route('/question/question_pdf_add/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def question_pdf_add(id):
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    get_exam = Examination.query.filter_by(id=id).first()
    division = Division.query.filter_by(id=get_exam.division_id).first()
    level = Level.query.filter_by(id=get_exam.level_id).first()
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file !')
            return redirect(url_for('admin.question_pdf_add', id=id))
        if request.form['minutes'] == '':
            flash('Duration cannot be empty !')
            return redirect(url_for('admin.question_pdf_add', id=id))
        duration_form = request.form['minutes'].replace(",", ".")
        check_format = duration_format_allowed(duration_form)
        if check_format is False :
            flash("Duration should be in numeric or decimal")
            return redirect(url_for('admin.question_pdf_add', id=id))
        duration = str(timedelta(minutes=float(duration_form)))
        user = User.query.filter_by(id=current_user.id).first()
        random_number = random.randint(1, 100000)
        timenow = str(datetime.now())
        mytime = timenow.split('.')
        filename = str(mytime[1])+ '_'+ str(user.id)+ '_' + str(user.level_id)+ '_' + str(user.division_id)+ '_' + str(random_number) +'.pdf'
        file.save(os.path.join(apps.config['UPLOAD_PATH'],filename))
        examination_detail = Examination_Detail()
        examination_detail.filename = filename
        examination_detail.duration = duration
        examination_detail.timedelta_duration = duration_form
        examination_detail.name = request.form['name']
        examination_detail.examination_id = id
        db.session.add(examination_detail)
        db.session.commit()
        return redirect(url_for('admin.question_pdf_data', id=id))
        
    return render_template('admin/examination_pdf/add.html', level=level, division=division, examination_id=id, exam_name=get_exam.name, get_exam=get_exam)

@admin.route('/question/question_pdf_edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def question_pdf_edit(id):
    # Check If user role is superadmin or admin
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    examination_detail = Examination_Detail.query.filter_by(id=id).first()
    get_exam = Examination.query.filter_by(id=examination_detail.examination_id).first()
    division = Division.query.filter_by(id=get_exam.division_id).first()
    level = Level.query.filter_by(id=get_exam.level_id).first()
    minutes = convert_in_minutes(str(examination_detail.duration))
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        user = User.query.filter_by(id=current_user.id).first()
        if file.filename != '':
            os.remove(os.path.join(apps.config['UPLOAD_PATH'], examination_detail.filename))
            random_number = random.randint(1, 100000)
            timenow = str(datetime.now())
            mytime = timenow.split('.')
            filename = str(mytime[1])+ '_'+ str(user.id)+ '_' + str(user.level_id)+ '_' + str(user.division_id)+ '_' + str(random_number) +'.pdf'
            file.save(os.path.join(apps.config['UPLOAD_PATH'],filename))
            examination_detail.filename = filename
        duration_form = request.form['minutes'].replace(",", ".")
        check_format = duration_format_allowed(duration_form)
        if check_format is False :
            flash("Duration should be in numeric or decimal")
            return redirect(url_for('admin.question_pdf_edit', id=id))
        duration = str(timedelta(minutes=float(duration_form)))
        examination_detail.name = request.form['name']
        examination_detail.duration = duration
        examination_detail.timedelta_duration = duration_form
        db.session.add(examination_detail)
        db.session.commit()
        return redirect(url_for('admin.question_pdf_data', id=get_exam.id))
        
    return render_template('admin/examination_pdf/edit.html', level=level, division=division, examination_id=id, get_exam=get_exam, exam_name=get_exam.name, examination_detail=examination_detail, minutes=minutes)


@admin.route('/question/question_pdf_delete/<id>', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def question_pdf_delete(id):
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    examination_detail = Examination_Detail.query.filter_by(id=id).first()
    os.remove(os.path.join(apps.config['UPLOAD_PATH'], examination_detail.filename))
    examination_detail.is_deleted = True
    db.session.add(examination_detail)
    db.session.commit()
    value = {
        "status": "00",
        "message": "Success"
    }
  
    # Dictionary to JSON Object using dumps() method
    # Return JSON Object
    return json.dumps(value)
    return redirect(url_for('admin.question_pdf_data', id=examination_detail.examination_id))

# dadasdssadsad
@admin.route('/test/result/', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def test_result():
    page = request.args.get('page', 1, type=int)
    _keyword = ""
    if current_user.role_id not in ADMIN_PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if request.method == "POST":
        _keyword= request.form['keyword']
        page = 1
    start = 0
    if page > 0:
        start = page * ROWS_PER_PAGE - ROWS_PER_PAGE
    _search = "%{}%".format(_keyword)
    directory = "/static/uploads/test/"
    page = request.args.get('page', 1, type=int)
    total_rows = Candidate_Test_Result.query.filter_by(is_deleted=False).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // - boxsize)
    test_result = db.session.query(User.id, User.fullname.label('name'), User.email, User.phone, Level.name.label('level'), Division.name.label('division'), Candidate_Test_Result.filename_psikotest.label('filename_psikotest'), Candidate_Test_Result.filename_maintest.label('filename_maintest')).join(Level, Division, Candidate_Test_Result, isouter=True).filter(Candidate_Test_Result.is_deleted.is_(False), User.fullname.like(_search)).order_by(User.id).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('admin.test_result', page=test_result.next_num) \
        if test_result.has_next else None
    prev_url = url_for('admin.test_result', page=test_result.prev_num) \
        if test_result.has_prev else None
    return render_template('admin/candidate/test_result.html', test_results=test_result.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages), directory=directory, start=start)
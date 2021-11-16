from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db, csrf
from ..models import *
from .forms import LoginForm
from datetime import datetime, date, time, timedelta

@auth.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    response = {}
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username = request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            response['status'] = '50'
            response['message'] = 'invalid username or password'
            return response
        if user.role.name.lower() == 'candidate':
            schedule = Candidate_Test_Schedule.query.filter_by(candidate_id=user.id).first()
            if schedule is not None :
                today = datetime.now()
                _date = today.strftime("%Y-%m-%d %H:%M:%S")
                date_today = datetime.strptime(_date, '%Y-%m-%d %H:%M:%S')
                _date_db = schedule.date_test.strftime("%Y-%m-%d %H:%M:%S")
                date_info = schedule.date_test.strftime("%d %m %Y %H:%M:%S")
                date_db = datetime.strptime(_date_db, '%Y-%m-%d %H:%M:%S')
                gs = Global_Setting.query.filter_by(setting_code=1).first()
                login_expired = date_db + timedelta(hours=int(gs.variable))
                print("today : ")
                print(date_today)
                print("login started : ")
                print(date_db)
                print("login expired : ")
                print(login_expired)
                print(date_db.date())
                print(date_today.date())
                print("=========================")
                if date_db.date() == date_today.date():
                    if date_today >= login_expired:
                        message = "Anda sudah melewati batas maksimal login"
                        status = '10'
                        response['status'] = status
                        response['message'] = message
                        return response
                    elif date_today < date_db:
                        message = "Anda belum diizinkan login. jadwal anda "+date_info
                        message = "Anda belum diizinkan login."
                        status = '20'
                        response['status'] = status
                        response['message'] = message
                        return response
                else:
                    message = "Anda sudah melewati batas maksimal login"
                    status = '50'
                    response['status'] = status
                    response['message'] = message
                    return response
            else:
                message = "Anda belum memiliki agenda test. Silahkan kontak kami"
                status = '30'
                response['status'] = status
                response['message'] = message
                return response
            response['status'] = '00'
            response['message'] = 'success'
            login_user(user)
            return response
        else:
            response['status'] = '00'
            response['message'] = 'User Found'
            login_user(user)
            return response
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

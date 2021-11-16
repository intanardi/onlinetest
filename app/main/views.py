from datetime import date, datetime
from flask import render_template, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import main
from .forms import NameForm
from .. import db
from ..models import User

directory = "/static/pdf/psikotest/soal_cfit.pdf"
ADMIN_PERMISSION_LIST = [1,2]
title = "Feniks CBT"

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_authenticated:
        if current_user.role.id not in ADMIN_PERMISSION_LIST:
            return redirect(url_for('candidate.index'))
        else :
            return redirect(url_for('admin.index'))
    return render_template('login.html')

@main.route('/test/psikotest', methods=['GET', 'POST'])
@login_required
def psikotest():
    if current_user.role.name.lower() != 'candidate':
        flash("You are not a candidate")
    now = datetime.utcnow()
    now = datetime.now()
    static = datetime(2021, 8, 10, 18, 00)
    test_time = static.strftime("%H:%M:%S")
    current_time = now.strftime("%H:%M:%S")
    d = datetime.now()
    unixtime = datetime.timestamp(static)*1000
    print(unixtime)
    # print(type(test_time))
    return render_template('exam/index.html', name=session.get('name'), knwon=session.get('known', False), current_time=current_time, directory=directory, test_time=unixtime)
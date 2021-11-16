from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template
from . import exam


@exam.route('/', methods=['POST', 'Get'])
@exam.route('/index', methods=['POST', 'Get'])
@login_required
def index():
    return render_template('candidate/exam/index.html')
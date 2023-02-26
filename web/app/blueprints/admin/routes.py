import pandas as pd
from flask import flash, redirect, url_for, request, \
    send_from_directory, current_app, render_template
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

import os
from app import db
from app.blueprints.admin import bp
from app.blueprints.admin.forms import AdminPassForm
from app.models import Upload

from app.util.helpers import is_admin, login_admin, logout_admin, redirect_url, allowed_file, admin_required


@bp.route('/', methods=["GET", "POST"])
@login_required
def admin():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(redirect_url())

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(redirect_url())
        if file and allowed_file(file.filename, {'sto'}):
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            upload = Upload(filename=filename)
            upload.user_id = current_user.id
            db.session.merge(upload)
            db.session.commit()
            return redirect(redirect_url())
    return render_template("admin/admin.html", is_admin=is_admin())


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin():
        return redirect(redirect_url())
    form = AdminPassForm()
    if form.validate_on_submit():
        if form.password.data == current_app.config['ADMIN_PASS']:
            login_admin()
            return redirect(url_for('admin.admin'))
        else:
            flash('Invalid password')
            return redirect(url_for('admin.login'))
    return render_template('admin/login.html', form=form)


@bp.route('/logout')
@admin_required
def logout():
    if is_admin():
        logout_admin()
    return redirect(url_for('admin.admin'))


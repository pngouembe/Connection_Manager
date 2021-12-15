from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import yaml

import sys
sys.path.append('../modules')
from resource_mgr import Resource
from user import User


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
#@login_required
def dashboard():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    with open("../config/resource_template.yml", "r") as f:
        rsrc_dict: dict = yaml.safe_load(f)
    rsrc_list = []
    for r in rsrc_dict["Resources"]:
        print(r["info"])
        rsrc_list.append(Resource(r["name"], r["info"]))
    return render_template("dashboard.html", resource_list=rsrc_list)


@views.route('/home')
def home():
    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

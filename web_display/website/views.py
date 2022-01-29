from os import name
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
# @login_required
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
    for r in rsrc_dict["resources"]:
        print(r["info"])
        rsrc_list.append(Resource(r["name"], r["info"]))
    rsrc_list[0].get_resource(
        User(user_info={"name": "toto", "comment": "salut"}))
    rsrc_list[0].get_resource(
        User(user_info={"name": "tata", "comment": "coucou"}))
    rsrc_list[0].get_resource(
        User(user_info={"name": "titi", "comment": "hello", "timeout": 30}))
    # rsrc_list[1].get_resource(
    #     User(user_info={"name": "testing with extra characters to see behavior", "comment": "Need to see if having a long message is breaking the display", "timeout": 10000000000}))
    # rsrc_list[1].get_resource(
    #     User(user_info={"name": "testing with extra characters to see behavior", "comment": "Need to see if having a long message is breaking the display", "timeout": 10000000000}))
    err = 0
    warn = 1
    info = 2
    dbg = 3
    log_buffer = [
        (err, "testing error logs"),
        (warn, "testing warn logs"),
        (info, "testing info logs"),
        (dbg, "testing debug logs")]
    for i in range(25):
        log_buffer.append((info, "testing info logs"))
    return render_template("dashboard.html", resource_list=rsrc_list, log_buffer=log_buffer)


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

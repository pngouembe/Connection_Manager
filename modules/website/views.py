from flask import Blueprint, render_template, request, flash
import yaml

import sys
sys.path.append('../modules')
from resource_mgr import Resource
from user import User


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def dashboard():
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

from flask import Blueprint, render_template, request, flash, current_app
import yaml

import sys
sys.path.append('../modules')
from resource_mgr import Resource, ResourceMgr
from user import User


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def dashboard():
    server: User = current_app.config.get('server_data')
    rsrc_list = server.get_resource_list()

    return render_template("dashboard.html", resource_list=rsrc_list)


@views.route('/home')
def home():
    return render_template("home.html", user=current_user)

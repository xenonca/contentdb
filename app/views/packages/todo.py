# Content DB
# Copyright (C) 2018  rubenwardy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from flask import *
from flask_user import *
from flask.ext import menu
from app import app
from app.models import *

@app.route("/todo/")
@login_required
def todo_page():
	canApproveNew = Permission.APPROVE_NEW.check(current_user)
	canApproveRel = Permission.APPROVE_RELEASE.check(current_user)

	packages = None
	if canApproveNew:
		packages = Package.query.filter_by(approved=False).all()

	releases = None
	if canApproveRel:
		releases = PackageRelease.query.filter_by(approved=False).all()

	return render_template("todo.html", title="Reports and Work Queue",
		approve_new=packages, releases=releases,
		canApproveNew=canApproveNew, canApproveRel=canApproveRel)

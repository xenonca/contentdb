from werkzeug.exceptions import abort

from app.logic.LogicError import LogicError
from app.logic.uploads import upload_file
from app.models import User, Package, PackageScreenshot, Permission, NotificationType, db
from app.utils import addNotification


def do_create_screenshot(user: User, package: Package, title: str, file):
	uploaded_url, uploaded_path = upload_file(file, "image", "a PNG or JPG image file")

	counter = 1
	for screenshot in package.screenshots:
		screenshot.order = counter
		counter += 1

	ss = PackageScreenshot()
	ss.package  = package
	ss.title    = title or "Untitled"
	ss.url      = uploaded_url
	ss.approved = package.checkPerm(user, Permission.APPROVE_SCREENSHOT)
	ss.order    = counter
	db.session.add(ss)

	msg = "Screenshot added {}" \
			.format(ss.title)
	addNotification(package.maintainers, user, NotificationType.PACKAGE_EDIT, msg, package.getDetailsURL(), package)
	db.session.commit()

	return ss


def do_order_screenshots(_user: User, package: Package, order: [any]):
	lookup = {}
	for screenshot in package.screenshots.all():
		lookup[screenshot.id] = screenshot

	counter = 1
	for id in order:
		try:
			lookup[int(id)].order = counter
			counter += 1
		except KeyError as e:
			raise LogicError(400, "Unable to find screenshot with id={}".format(id))
		except ValueError as e:
			raise LogicError(400, "Invalid number: {}".format(id))

	db.session.commit()

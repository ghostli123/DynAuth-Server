from flask import Blueprint, request, abort, current_app
from geoauth.forms import LocationUpdateForm, LocationRegionForm, DeviceRegistrationForm, DeviceKeyRequestForm
from geoauth.models import Device, DeviceKey, DeviceLocationUpdate, \
    DeviceLocationRegion, APIAccount, APIKey, UserAccount
import dateutil.parser

device_api_blueprint = Blueprint("geoauth_device_api", __name__)


@device_api_blueprint.route('/device/check-in', methods=['POST'])
def check_in():
    form = LocationUpdateForm(csrf_enabled=False)
    if form.validate_on_submit():
        device = Device.query.filter(Device.uuid == form.device_id.data).first()
        if device is None:
            abort(404)
        loc_upd = DeviceLocationUpdate(device, form.latitude.data, form.longitude.data, dateutil.parser.parse(form.time.data))
        current_app.db.session.add(loc_upd)
        current_app.db.session.commit()

        return "OK"
    else:
        print form.errors
        print form.time.data
        print request.form['time']
        abort(400)


@device_api_blueprint.route('/device/add-region', methods=['POST'])
def add_region():
    form = LocationRegionForm(csrf_enabled=False)
    if form.validate_on_submit():
        device = Device.query.filter(Device.uuid == form.device_id.data).first()
        if device is None:
            abort(404)
        reg_upd = DeviceLocationRegion(device, form.latitude.data, form.longitude.data, form.time.data, form.name.data)
        current_app.db.session.add(reg_upd)
        current_app.db.session.commit()

        return "OK"
    else:
        abort(400)


@device_api_blueprint.route('/device/register', methods=['POST'])
def register_device():
    form = DeviceRegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        user = UserAccount.query.filter(UserAccount.username == form.username.data).first()
        if user is None:
            abort(403)
        if not user.authenticate(form.password.data):
            abort(403)
        dkey = DeviceKey.query.filter(DeviceKey.key == form.device_key.data) \
                              .filter(DeviceKey.activated == False).first()
        if dkey is None:
            abort(403)

        device = dkey.use_key(form.device_name.data, user)
        current_app.db.session.add(device)
        current_app.db.session.add(dkey)
        current_app.db.session.commit()

        return device.uuid
    else:
        abort(400)
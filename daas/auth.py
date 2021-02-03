import base64
from functools import wraps
import json

from flask import abort, Blueprint, request

from .exts import db
from .models import User

auth = Blueprint("auth", __name__)

def _generate_api_key():
    with open("/dev/urandom", "rb") as f:
        r = f.read(32)
    
    key = base64.b64encode(r).decode()

    return key

# decorator to ensure valid credentials
def auth_required(f):
    @wraps(f)
    def check_auth(*args, **kwargs):
        header = request.headers.get("Authorization")
        if header is None:
            return {"status": "error", "msg": "bad auth"}, 403

        try:
            key = header.split("Bearer ")[1]
        except IndexError:
            return {"status": "error", "msg": "bad auth"}, 403

        user = User.query.filter_by(apikey=key).first()
        if not user:
            return {"status": "error", "msg": "bad auth"}, 403

        return f(*args, **kwargs)
    return check_auth 

# generate an account if there aren't any
# if there are any rows in the `user` table, this should 403
@auth.route("/auth/setup_acc", methods=["POST"])
def setup_acc():
    num_rows = db.session.query(User).count()

    if num_rows > 0:
        abort(403)

    key = _generate_api_key()

    new_user = User(apikey=key, desc="account from /auth/gen_first_acc")

    db.session.add(new_user)
    db.session.commit()

    return {"status": "ok", "apikey": key}

# add a new user
@auth.route("/auth/register", methods=["POST"])
@auth_required
def register():
    body = request.json

    if body is None:
        return {"status": "error", "msg": "need to specify desc"}, 400

    if "desc" not in body.keys():
        return {"status": "error", "msg": "need to specify desc"}, 400

    if len(body["desc"]) > User.desc.property.columns[0].type.length:
        return {"status": "error", "msg": "desc too long"}, 400
    
    key = _generate_api_key()

    new_user = User(apikey=key, desc=body["desc"])

    db.session.add(new_user)
    db.session.commit()

    return {"status": "ok", "apikey": key}

import base64

from flask import abort, Blueprint

from .exts import db
from .models import User

auth = Blueprint("auth", __name__)

def _generate_api_key():
    with open("/dev/urandom", "rb") as f:
        r = f.read(32)
    
    key = base64.b64encode(r).decode()

    return key

# generate an account if there aren't any
# if there are any rows in the `user` table, this should 403
@auth.route("/auth/gen_first_acc")
def gen_first_acc():
    num_rows = db.session.query(User).count()

    if num_rows > 0:
        abort(403)

    key = _generate_api_key()

    new_user = User(apikey=key, desc="account from /auth/gen_first_acc")

    db.session.add(new_user)
    db.session.commit()

    return key

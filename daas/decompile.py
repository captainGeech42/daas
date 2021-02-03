import base64

from flask import Blueprint

from .exts import db
from .models import User

decompile = Blueprint("decompile", __name__)

@decompile.route("/request_decomp")
def request_decomp():
    pass

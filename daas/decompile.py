import base64
import os
import random
import shutil
import string
import subprocess
import _thread

from flask import Blueprint, request

from .exts import db
from .models import Binary, DecompilationStatus
from .auth import auth_required

BINARY = "binary"
DECOMP_OUTPUT = "output.c"

decompile = Blueprint("decompile", __name__)

def _decompile_binary(id, bindir):
    # ATTN: DB CODE SHOULD BE MADE MULTITHREADED
    # CURRENTLY IT IS NOT BECAUSE I AM LAZY
    # WHEN IT BECOMES MT COMPATIBLE, UNCOMMENT THIS STUFF

    #row = Binary.query.filter_by(id=id).first()
    #if row is None:
    #    return False

    try:
        input_path = os.path.join(bindir, BINARY)
        output_path = os.path.join(bindir, DECOMP_OUTPUT)

        # decompile with a 5 minute timeout
        #subprocess.run(["/ida/idat64", "-A", '-S"/decompile.py \\"--output\\" \\"{output_path}\\""', input_path], env={"TERM":"XTERM"}, timeout=300)
        #subprocess.run(["/ida/idat64", "-A", f'-S"/decompile.py \\"--output\\" \\"{output_path}\\""', input_path], timeout=300)
        os.system(f'/ida/idat64 -A -S"/decompile.py \\"--output\\" \\"{output_path}\\"" {input_path}')

        # decompliation succeeded
        #row.status = DecompilationStatus.completed
    except subprocess.TimeoutExpired:
        # decompilation timed out
        #row.status = DecompilationStatus.failed
        pass

    # save row update
    #db.session.commit()

def _spawn_decompilation_thread(id, bindir):
    try:
        _thread.start_new_thread(_decompile_binary, (id, bindir))
    except:
        return False

    return True

def _gen_dir():
    keyspace = string.ascii_letters

    dirname = f"/tmp/" + "".join([random.choice(keyspace) for _ in range(10)])

    if not os.path.isdir(dirname):
        os.mkdir(dirname)
        return dirname
    else:
        return _gen_dir()

@decompile.route("/request_decomp", methods=["POST"])
@auth_required
def request_decomp():
    # parse out the binary

    body = request.json

    if body is None:
        return {"status": "error", "msg": "need to specify binary and requestor"}, 400

    if "binary" not in body.keys():
        return {"status": "error", "msg": "need to specify binary"}, 400

    if "requestor" not in body.keys():
        return {"status": "error", "msg": "need to specify binary"}, 400

    binary = base64.b64decode(body["binary"])

    # save the binary to disk
    dirname = _gen_dir()

    with open(os.path.join(dirname, BINARY), "wb") as f:
        f.write(binary)

    # add to database
    rec = Binary(requestor=body["requestor"], status=DecompilationStatus.queued, output_dir=dirname)
    db.session.add(rec)
    db.session.commit()

    # spawn thread
    if _spawn_decompilation_thread(rec.id, dirname):
        return {"status": "ok", "msg": "started analysis", "id": rec.id}
    else:
        return {"status": "err", "msg": "failed to start analysis"}, 500

@decompile.route("/status/<id>")
@auth_required
def status(id=0):
    binary = Binary.query.filter_by(id=id).first()

    if not binary:
        return {"status": "err", "msg": f"failed to find binary {id}"}, 404

    # check if there is decomp
    path = os.path.join(binary.output_dir, DECOMP_OUTPUT)
    if os.path.isfile(path):
        # see if the file has stuff
        with open(path, "r") as f:
            contents = f.read()

        if len(contents.split()) > 10:
            binary.status = DecompilationStatus.completed
            db.session.commit()

    return {"status": "ok", "analysis_status": str(binary.status).split(".")[1]}

@decompile.route("/get_decompilation/<id>")
@auth_required
def get_decompilation(id=0):
    binary = Binary.query.filter_by(id=id).first()

    if not binary:
        return {"status": "err", "msg": f"failed to find binary {id}"}, 404

    if binary.status != DecompilationStatus.completed:
        return {"status": "err", "msg": "decompilation not finished, did you check the status?"}, 400

    if binary.status == DecompilationStatus.removed:
        return {"status": "err", "msg": "decompilation was already returned, please re-request"}, 400

    try:
        with open(os.path.join(binary.output_dir, DECOMP_OUTPUT), "r") as f:
            decomp = f.read()
    except FileNotFoundError:
        return {"status": "err", "msg": "decompilation not found"}, 500

    # delete binary to prevent disk from filling up
    shutil.rmtree(binary.output_dir)
    binary.status = DecompilationStatus.removed
    db.session.commit()

    return {"status": "ok", "output": base64.b64encode(decomp.encode()).decode()}

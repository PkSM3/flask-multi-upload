from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
from uuid import uuid4

app = Flask(__name__)

#app.TWJSrealmainpath = "/home/pksm3/www"
#app.TWJSlocalpath = "/i7/CNRS/"
#app.TWJSdata = "data"

app.TWJSrealmainpath = "/var/www"
app.TWJSlocalpath = "/CNRSdemo"
app.TWJSdata = "data"
app.serverpath = "http://tina.iscpif.fr"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/trial")
def trial():
    from uploadr.phylo_gexf2json import PhyloGen
    # print "printing: "+PhyloGen.something()
    instance = PhyloGen()
    returnvar = instance.something()
    return render_template("trial.html")

@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.

    twjspath = app.TWJSrealmainpath+app.TWJSlocalpath+"/"+app.TWJSdata
    target = twjspath+"/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    print "=== Form Data ==="
    for key, value in form.items():
        print key, "=>", value

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print "Accept incoming file:", filename
        print "Save it to:", destination
        upload.save(destination)
        from uploadr.phylo_gexf2json import PhyloGen
        phylolayout = PhyloGen()
        returnvar = phylolayout.process(destination)
        print "\tjson guardado en:"
        print "\t"+returnvar
        print " - - - -"

    # return ajax_response(True, upload_key)
    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key))


@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    twjspath = app.TWJSrealmainpath+app.TWJSlocalpath+"/"+app.TWJSdata
    root = twjspath+"/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    json_file = ""
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split("/")[-1]
        if ".json" in fname: json_file = fname
        files.append(fname)

    print "root: "+ root
    print "json_file: "+json_file
    folder_file = "/".join( [app.TWJSdata,uuid,json_file] )
    print "folder_file: "+folder_file
    print " - - - - - - - "



    return render_template("files.html",
        uuid=uuid,
        files=files,
        path=folder_file,
        url=(app.serverpath+app.TWJSlocalpath),
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))

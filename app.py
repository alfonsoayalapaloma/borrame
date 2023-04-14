import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for, flash 
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


import threading
import sys

from werkzeug.utils import secure_filename
#
import subprocess 
from subprocess import Popen
from subprocess import PIPE
from itertools import islice
from threading import Thread
from queue import Queue, Empty
#
from flask import jsonify


WORKERS=1
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

JOB_LOG=""
#app = Flask(__name__)



app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.JOB_LOG=""
app.COMMANDS=""
    
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Token


@app.route('/ping/<address>', methods=['GET'])
def ping(address=""):
    answer="ERROR: No fue posible ejecutar el ping."
    if address !="":
        cmd="ping -c5 "+address
        answer=run_cmd(cmd)
    return jsonify({"command":"ping", "address":address,'result':str(answer)})


@app.route('/traceroute/<address>', methods=['GET'])
def traceroute(address=""):
    answer="ERROR: No fue posible ejecutar el trace."
    if address !="":
        cmd="traceroute "+address
        answer=run_cmd(cmd)
    return jsonify({"command":"traceroute", "address":address,'result':str(answer)})

def run_cmd(cmd=""):
    output=""
    if cmd!="":
        print(cmd)
        p=os.popen(cmd)
        #print(p)
        output = p.read()
        #print(output)
        strdate="2023-04-12 00:00:00"
        app.JOB_LOG=app.JOB_LOG+"\n"+ strdate  
        app.JOB_LOG=app.JOB_LOG+"\n"+output
        print("job-log:"+app.JOB_LOG+"|||")
    return output        



@app.route('/pinglist/', methods=['GET', 'POST'])
@csrf.exempt
def ping_list():
    #shell=""    
    if request.method == 'POST':
        commands = request.form.get('commands')
        app.COMMANDS=commands
        app.JOB_LOG=""
        #shell=request.form.get('shell')        
                
        q = Queue(maxsize = 1024)
        print("queue created.")        
        for i in range(WORKERS):
            t = Thread(target=worker, args=[q])
            t.daemon = True
            t.start()
        for item in commands.split("\n"):
            q.put(item)        
        q.join()       # block until all tasks are done                
                
    return render_template('change_dns.html', shell=app.JOB_LOG, commands=app.COMMANDS)

def worker(q):
    while True:
        item = q.get()
        do_work(item)
        q.task_done()

def do_work(item):
        cmd = "python /usr/share/cmapi/changecmdns.py "+ item
        #print(cmd)
        p=os.popen(cmd)
        #print(p)
        output = p.read()
        #print(output)
        strdate="2023-04-12 00:00:00"
        app.JOB_LOG=app.JOB_LOG+"\n"+ strdate  
        app.JOB_LOG=app.JOB_LOG+"\n"+output
        print("job-log:"+app.JOB_LOG+"|||")
        return output        


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
                               
####
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@csrf.exempt
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #f = request.files['file'] puts the uploaded file (in the request) to a var ("f"). Then 
            content=file.read()
            return content #redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

from flask import send_from_directory

@app.route('/uploads/<name>')
@csrf.exempt
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)    
                               

if __name__ == '__main__':
    #app.run()
    app.run(host="0.0.0.0", port=80)
    #app.run(debug=True, port=8001)

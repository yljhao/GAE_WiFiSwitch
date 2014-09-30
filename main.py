from flask import Flask

# For file sending and basic http auth
from functools import wraps
from flask import request, Response, send_file

# For data storing
from google.appengine.ext import ndb

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

"""
Reference :

Database model class
https://cloud.google.com/appengine/docs/python/ndb/modelclass
Database data finding class
https://cloud.google.com/appengine/docs/python/ndb/queryclass
Database key operate class
https://cloud.google.com/appengine/docs/python/ndb/keyclass


http://stackoverflow.com/questions/14458470/google-app-engines-ndb-get-an-entitys-id
http://stackoverflow.com/questions/12220653/get-ndb-query-length-using-python-on-google-app-engine

Confuse part:
https://cloud.google.com/appengine/docs/python/ndb/entities


Another way to do so:

class Data_store(ndb.Model):
	status = ndb.StringProperty()

def Write_data(data_string):
	data = Data_store(id = "Switch", status = data_string)
	data.put()

def Read_data():
	data = Data_store.get_by_id("Switch")
	if(data):
		return data.status
	else:
		return ""

"""

### This section is for data storage ###
class Data_store(ndb.Model):
	name = ndb.StringProperty()
	status = ndb.StringProperty()

def Write_data(data_string):
	# Find dataname first.
	data = Data_store.query(Data_store.name == "Switch").get()
	if(data):
		# Find dataname in database, update it.
		data.status = data_string
	else:
		# Cannot find dataname in database, create it.
		data = Data_store(name = "Switch", status = data_string)
	data.put()

def Read_data():
	data = Data_store.query(Data_store.name == "Switch").get()
	return data.status

"""
Reference:

http://flask.pocoo.org/snippets/8/

"""
### This section is for basic auth ###

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    # Don't forget change username and password for weblogin.
    return username == 'admin' and password == 'password'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


"""
Reference :

POST route:
http://stackoverflow.com/questions/10313001/is-it-possible-to-make-post-request-in-flask
http://stackoverflow.com/questions/10434599/how-can-i-get-the-whole-request-post-body-in-python-with-flask
http://flask.pocoo.org/docs/0.10/quickstart/

send_file:
http://stackoverflow.com/questions/8637153/how-to-return-images-in-flask-response

send_fromdirectory:
http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask

"""
### This section is for web application ###
@app.route('/logo.png')
@requires_auth
def logo():
	return send_file('files/logo.png')

@app.route('/status')
def status():
	return Read_data()

@app.route('/Onload', methods=['POST'])
@requires_auth
def onload():
    return Read_data()

@app.route('/SWON', methods=['POST'])
@requires_auth
def on():
    Write_data('Switch ON')
    return Read_data()

@app.route('/SWOFF', methods=['POST'])
@requires_auth
def off():
    Write_data('Switch OFF')
    return Read_data()

@app.route('/', methods=['GET'])
@requires_auth
def index():
    """Return a friendly HTTP greeting."""
    return send_file('files/index.html')


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

from flask import Flask, request,jsonify,render_template
import json
from flask_socketio import SocketIO,emit
import pymongo
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB = os.getenv('MONGO_DB')

mongo_uri = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@{os.environ['MONGO_HOST']}/?retryWrites=true&w=majority"

client = pymongo.MongoClient(mongo_uri)

# database = client[MONGO_DB]
# collection = database['events']
# collection_user_events = database['userevents']

database = "mandrill_db"
db = client.database
collection = db['events']
collection_user_events=db['userevents']

app = Flask(__name__)
SECRET_KEY = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)

previous_doc = None

@socketio.on('connect')
def on_connect():
    print('WebSocket client connected')

@app.route('/')
def index():
    """This is a Flask route that returns the index.html template,
     which contains the frontend code for the WebSocket client."""
    return render_template('index.html')

@socketio.on('disconnect')
def on_disconnect():
    """This is a Flask-SocketIO event handler that gets called whenever a WebSocket client disconnects from the Flask app.
     In this implementation, it simply prints a message to the console."""
    print('WebSocket client disconnected')

@app.route('/check_new_entries')
def check_collection():
    """This is a Flask route that checks the MongoDB collection every 30 seconds for new entries.
     If a new entry is found, it emits a WebSocket message to all connected clients with the document ID
      and email subject, and returns the latest document as an HTML template.
    Otherwise, it returns a message indicating that there are no new entries in the collection."""
    global previous_doc
    with app.app_context():
    # Get the latest document from the collection
        try:
            latest_doc = collection_user_events.find_one(sort=[('_id', pymongo.DESCENDING)])
            # Check if the latest document is different from the previous document
            # (assuming the collection is sorted by _id in descending order)
            if latest_doc != previous_doc and latest_doc.get('event_open',True):
                # Store the latest document as the previous document for the next check
                previous_doc = latest_doc
                # Return the document value in an HTML template
                print('returning document',latest_doc)
                print(str(latest_doc['_id']))
                print(latest_doc['subject'])
                # Publish a message to the WebSocket with the document ID and the email subject

                with app.app_context():
                    # emit notification to clients
                    socketio.emit('notification', {'id': str(latest_doc['_id']), 'subject': latest_doc['subject']})
                # emit('notification', {'id': str(latest_doc['_id']), 'subject': latest_doc['subject']})
                return render_template('index.html',document=latest_doc)
            else:
                # Return a message indicating that there are no new entries in the collection
                print('No new entry in table.')
                return 'No new entry in table.'
        except Exception as e:
            # Use the traceback module to print the full traceback of the error
            traceback.print_exc()
            return 'An error occurred while checking the collection.'


@app.route('/send_mail',methods=['POST'])
def send_mail():
    """
    This is a Flask route that handles POST requests for sending emails. It extracts the necessary data from the request payload,
    inserts the email response into the collection MongoDB collection, and returns the response as a JSON object.
    :return:{"email": "rastogiprakhar01@gmail.com", "status": "sent", "reject_reason": [""], "queued_reason": [""], "_id": "12356"}
    """
    headers = {'Content-Type': 'application/json'}
    data=request.get_json()
    response={}
    response['email']=data['from_email']
    response['status']='sent'
    response['reject_reason']='',
    response['queued_reason']='',
    response['_id']=data['metadata']['message_id']
    collection.insert_one(response)
    print('connection established to DB')
    result = json.dumps(response)
    return result

@app.route('/get_mail',methods=['GET'])
def get_mail():
    """This is a Flask route that handles GET requests for retrieving all email responses
     from the collection MongoDB collection. It returns an HTML template that displays the email responses."""
    data = []
    for doc in collection.find():
        data.append(doc)
    print(data,'Data')
    return render_template('mails.html',response=data)


@app.route('/user_events',methods=['POST'])
def user_events():
    """
     This is a Flask route that handles POST requests for inserting email event data into the collection_user_events MongoDB collection.
     It extracts the necessary data from the request payload, inserts the data into the collection_user_events MongoDB collection,
     and returns the data as a JSON object.
    :return:{"email": "rastogiprakhar01@gmail.com", "subject": "Example Subject", "_id": "12356", "event_open": true}
    """
    headers = {'Content-Type': 'application/json'}
    data = request.get_json()
    response = {}
    response['email'] = data['from_email']
    response['subject'] = data['subject']
    response['_id'] = data['metadata']['message_id']
    response['event_open'] = data['tracks_opens']
    collection_user_events.insert_one(response)
    print('connection established to DB')
    result = json.dumps(response)
    print(result)
    return result

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_collection, 'interval', seconds=30)
    scheduler.start()
    # app.run(debug=True)
    socketio.run(app,allow_unsafe_werkzeug=True)
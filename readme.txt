
Problem Statement
------------------

● Mandrill sends event [open] to backend app webhook 
● Backend stores message payload into storage of some kind (cache/sql/nosql 
or any other, no schema definition required). Mandrill’s message ID can be 
used as a key 
● Backend publishes notification that user opened email via websocket to very 
simple index.html frontend with websocket client 
(https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

-------------------------------------------------------------
Requirements 
● Python 3.10+ as a backend language (preferably)- Python 3.10+ used
● Any backend framework that supports websockets - Flask Framework used
● Some sort of repo or zip of everything, whatever is easiest - Github and zip both options provided.

----------------------------------------------------------


Approach used
----------------------

Dummy api created to mimic sending mails and response stored in Mongodb.
Another api created to capture email open events ( Assuming user open's email manually , so in our case we will trigger POST api manually and store response in collection user_events)
Scheduler is created which checks for OPEN events received from user_events api every 30 secs.
if the event is received , it publishes message_id and subject of message to index.html.

------------------------------------------------------------------------------------------------------



	

Code Explanation
-------------------------------------
The code starts by importing the necessary libraries including Flask, Flask-SocketIO, pymongo, traceback, requests, and apscheduler.

It then creates a client connection to the MongoDB database using the pymongo.MongoClient() method and assigns the database and collection to db and collection variables, respectively.
Next, it defines an instance of the Flask application and configures it with a secret key. 

It then creates an instance of SocketIO and passes in the Flask app object as an argument.

The code then defines a global variable previous_doc to store the previously checked document from the MongoDB collection.

It then defines a route / that renders the index.html template file.

Next, it defines a socketio.on('connect') event handler that prints a message to the console when a WebSocket client connects to the server.

It also defines a socketio.on('disconnect') event handler that prints a message to the console when a WebSocket client disconnects from the server.

The check_collection() function is defined to periodically check for new entries in the MongoDB collection. It uses the collection_user_events.find_one() method to retrieve the latest document in the collection sorted by _id in descending order.

If the latest document is different from the previous document and the event_open field is True, it stores the latest document as the previous document, emits a notification message to all connected clients via the WebSocket, and returns the latest_doc object to the index.html template for rendering.

The send_mail() function handles the POST request to send an email. It retrieves the email data from the POST request and inserts it into the MongoDB collection using the collection.insert_one() method.

The get_mail() function handles the GET request to retrieve all the emails from the MongoDB collection. It retrieves all the documents from the collection using the collection.find() method and returns the data to the mails.html template for rendering.

The user_events() function handles the POST request to insert user events into the MongoDB collection_user_events. It retrieves the user event data from the POST request and inserts it into the MongoDB collection_user_events using the collection_user_events.insert_one() method.

Finally, the code starts a background scheduler that executes the check_collection() function every 30 seconds to periodically check for new entries in the MongoDB collection. It then starts the Flask application by calling socketio.run() method with the allow_unsafe_werkzeug=True parameter.

----------------------------------------------------------------------------

Example of Resquest and Response used in below apis are:

http://127.0.0.1:5000/send_mail
http://127.0.0.1:5000/user_events

Request:

{"subject": "Example Subject", "from_email": "rastogiprakhar01@gmail.com", "from_name": "Sender Name", "to": [{"email": "rastogiprakhar01@gmail.com"}], "html": "<p> Example html Content</p>", "headers": {"Reply-To": "rastogiprakhar01@gmail.com"}, "tracks_opens": true, "metadata": {"message_id": "12359"}, "url": "https://b708-2401-4900-1c3c-c071-26-636b-2e23-6a27.in.ngrok.io/mandrill_webhook"}

Response:

{"email": "rastogiprakhar01@gmail.com", "subject": "Example Subject", "_id": "12359", "event_open": true}

--------------------------------------------------------------------------------------------------------------------







# CHAT-API 
This project is a simple chat application developed in Flask, a lightweight python web development framework. This API can be used to create users,
send messages and like messages sent by other users. The list of messages sent can be viewed along with the their respective like count.
This is a basic application and hence, features like sending messages to a particular user, authentication and authorization are not included. 

## Requirements ##

- [x] Python 3.10
- [x] Flask 2.2
- [x] psycopg2-binary

The database used in this API is postgreSQL, taken from ElephantSQL which offers postgreSQL as a service. 

## Usage ##

To run this app, install the latest version of Python3. After that, install all the dependencies from the command line.

```shell
pip install -r requirements.txt
```

Run the app.py file after setting up your connection to the database. The development server runs on the localhost port 5000. Copy the url from the command line
and test the endpoints of the API using services like Postman, Insomnia etc. The data format of the response is in the form of JSON.

#### API Endpoints 

###### Home page /

This url returns all the messages with the most recent messages first.

###### /send_message/<int:user_id>

This url is used to POST a message by the specified user to the database.

###### /create_user

This url is used to create a user by entering the username.

###### /<int:user_id>/<int:message_id>

This url is used to like or unlike a message sent by the user. This endpoint assumes that the 'Like' button on the front-end is a boolean field, like a checkbox.

###### /get_likes

This url returns the no. of likes corresponding to each message. 




from flask import Flask, request
import os
import psycopg2
from dotenv import load_dotenv
import json

load_dotenv()


app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

#Required SQL Queries
CREATE_USERS_TABLE = """CREATE TABLE IF NOT EXISTS "user" (user_id SERIAL PRIMARY KEY,username TEXT);"""

CREATE_MESSAGES_TABLE = """CREATE TABLE IF NOT EXISTS "message" (message_id SERIAL PRIMARY KEY, 
                            user_id INT NOT NULL,
                            message TEXT,
                            like_count INT DEFAULT 0,
                            FOREIGN KEY(user_id) REFERENCES "user"(user_id) ON DELETE CASCADE);"""

CREATE_LIKES_TABLE = """CREATE TABLE IF NOT EXISTS "likes" (id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        message_id INT NOT NULL,
                        like_flag INT NOT NULL,
                        FOREIGN KEY(message_id) REFERENCES "message"(message_id) ON UPDATE CASCADE);"""

INSERT_INTO_USERS = """INSERT INTO "user" (username) VALUES (%s) RETURNING user_id;"""

INSERT_INTO_MESSAGES = """INSERT INTO "message" (message,user_id) VALUES (%s, %s) RETURNING message_id;"""

INSERT_INTO_LIKES = """INSERT INTO "likes" (user_id, message_id, like_flag) VALUES (%s, %s, %s);"""

GET_MESSAGES = """SELECT * FROM "message" ;"""

UPDATE_LIKES_TRIGGER = """CREATE OR REPLACE FUNCTION increment_likes() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.like_flag = 1 THEN
        UPDATE "message" SET like_count = like_count + 1 WHERE message_id = NEW.message_id;
    ELSIF NEW.like_flag = 0 THEN
        UPDATE "message" SET like_count = like_count - 1 WHERE message_id = NEW.message_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS increment_likes on "likes";
CREATE TRIGGER increment_likes
AFTER INSERT ON likes
FOR EACH ROW
EXECUTE FUNCTION increment_likes();
"""

GET_LIKES = """SELECT message_id, message, like_count FROM "message"; """

with connection:
    with connection.cursor() as con:
        con.execute(CREATE_USERS_TABLE)
        con.execute(CREATE_LIKES_TABLE)
        con.execute(CREATE_MESSAGES_TABLE)


@app.route('/', methods = ["GET"])
def get_messages():
    with connection:
        with connection.cursor() as con:
            con.execute(GET_MESSAGES)
            data = [dict((con.description[i][0], value) \
            for i, value in enumerate(row)) for row in con.fetchall()]
    if len(data) == 0:
        return json.dumps({'Message':'No messages present'}), 404
    return json.dumps(data), 200

@app.route('/get_likes', methods = ["GET"])
def get_likes():
    with connection:
        with connection.cursor() as con:
            con.execute(GET_LIKES)
            data = [dict((con.description[i][0], value) \
            for i, value in enumerate(row)) for row in con.fetchall()]
    if(len(data)==0):
        return json.dumps({'Message':'No data'}), 404
    return json.dumps(data), 200


@app.route('/create_user' , methods = ["POST"])
def create_user():
    username = request.form["username"]
    with connection:
        with connection.cursor() as con:
            con.execute(INSERT_INTO_USERS,(username,))
            user_id = con.fetchone()[0]
    return json.dumps({"id":user_id, "username":username}), 201

@app.route('/send_message/<int:user_id>', methods = ["POST"])
def send_message(user_id:int):
    message = request.form["message"]
    with connection:
        with connection.cursor() as con:
            con.execute("""SELECT username FROM "user" WHERE user_id = {}""".format(user_id))
            data = con.fetchall()
            if not data:
                return json.dumps({'Error': "User doesn't exist"}),404
            else:
                con.execute(INSERT_INTO_MESSAGES, (message, user_id,))
                message_id = con.fetchone()[0]
    return json.dumps({"id":message_id, "Status": "Successfully posted"}), 201

@app.route('/<int:user_id>/<int:message_id>',methods = ["POST"])
def like_message(user_id:int, message_id:int):
    like = int(request.form["like"])
    with connection:
        with connection.cursor() as con:
            con.execute("""SELECT username FROM "user" WHERE user_id = {}""".format(user_id))
            user = con.fetchall()
            con.execute("""SELECT message FROM "message" WHERE message_id = {}""".format(message_id))
            msg = con.fetchall()
            if not user or not msg:
                return json.dumps({'Error': 'Invalid credentials'}), 404
            else:
                con.execute(UPDATE_LIKES_TRIGGER)
                con.execute(INSERT_INTO_LIKES,(user_id,message_id,like))
    return {"Status":"Liked the post"}, 201

if __name__ == '__main__':
    app.run()
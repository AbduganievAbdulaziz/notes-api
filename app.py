import os 
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

CREATE_NOTES_TABLE = """CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        title TEXT,
                        content TEXT
                    );"""

GET_NOTES = "SELECT id, title, content FROM notes ORDER BY id ASC;"

INSERT_NOTE_RETURN_ID = "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING *;"

UPDATE_NOTE = """UPDATE notes
                 SET title = %s, content = %s
                 WHERE id = %s
                 RETURNING *;"""

DELETE_NOTE = "DELETE FROM notes WHERE id = %s;"

load_dotenv()

app = Flask(__name__)
cors = CORS(app, origins='*')
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get("/")
def get_notes():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_NOTES_TABLE)
            cursor.execute(GET_NOTES)
            notes = cursor.fetchall()
            result = []
            for note in notes:
                result.append({"id": note[0], "title": note[1], "content": note[2]})
            return jsonify(result)

@app.post("/")
def add_note():
    data = request.get_json()
    title = data["title"]
    content = data["content"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_NOTE_RETURN_ID, (title, content))
            t = cursor.fetchone()
            new_note = {"id": t[0], "title": t[1], "content": t[2] }
            return jsonify(new_note)

@app.put("/<int:note_id>")
def update_note(note_id):
    data = request.get_json()
    new_title = data["title"]
    new_content = data["content"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_NOTE, (new_title, new_content, note_id))
            updated_note = cursor.fetchone()
            return {"id": updated_note[0], "title": updated_note[1], "content": updated_note[2]}

@app.delete("/<int:note_id>")
def delete_note(note_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_NOTE, (note_id, ))
            return {"id": note_id}
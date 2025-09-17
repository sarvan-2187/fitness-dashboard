from flask import Flask, render_template, request, redirect, jsonify, Response
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
DATA_FILE = 'data.json'

GENAI_API_KEY = os.environ.get("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise RuntimeError("GENAI_API_KEY not set. Please set it in environment variables.")

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class FitnessLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None  # Tail pointer for O(1) append operations

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def delete_by_date(self, date):
        temp = self.head
        prev = None
        while temp:
            if temp.data['date'] == date:
                if prev:
                    prev.next = temp.next
                else:
                    self.head = temp.next
                if temp == self.tail:
                    self.tail = prev
                return
            prev = temp
            temp = temp.next

    def to_list(self):
        result = []
        temp = self.head
        while temp:
            result.append(temp.data)
            temp = temp.next
        return result

    def load_from_list(self, data_list):
        self.head = None
        self.tail = None
        for data in data_list:
            self.append(data)

    def get_last_entry(self):
        return self.tail.data if self.tail else None

    def get_first_entry(self):
        return self.head.data if self.head else None

    def is_empty(self):
        return self.head is None

    def size(self):
        count = 0
        temp = self.head
        while temp:
            count += 1
            temp = temp.next
        return count


def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except:
        return []


def save_data(data_list):
    with open(DATA_FILE, 'w') as file:
        json.dump(data_list, file, indent=4)


@app.route('/')
def index():
    raw_data = load_data()
    fitness_list = FitnessLinkedList()
    fitness_list.load_from_list(raw_data)
    return render_template('index.html', entries=fitness_list.to_list())


@app.route('/add', methods=['POST'])
def add_entry():
    entry = {
        'date': request.form['date'],
        'steps': int(request.form['steps']),
        'calories': int(request.form['calories']),
        'distance': float(request.form['distance']),
        'active_minutes': int(request.form['active_minutes'])
    }
    raw_data = load_data()
    fitness_list = FitnessLinkedList()
    fitness_list.load_from_list(raw_data)
    fitness_list.append(entry)
    save_data(fitness_list.to_list())
    return redirect('/')


@app.route('/delete', methods=['POST'])
def delete_entry():
    date = request.form['date']
    raw_data = load_data()
    fitness_list = FitnessLinkedList()
    fitness_list.load_from_list(raw_data)
    fitness_list.delete_by_date(date)
    save_data(fitness_list.to_list())
    return redirect('/')


@app.route('/device')
def device():
    return render_template('device.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/chat', methods=['POST'])
def chat_response():
    message = request.json.get('message')
    result = model.generate_content(message)
    return jsonify({'response': result.text})


@app.route('/export')
def export_csv():
    raw_data = load_data()
    if not raw_data:
        return "No data to export", 404

    csv_output = "Date,Steps,Calories,Distance,Active Minutes\n"
    for entry in raw_data:
        csv_output += f"{entry['date']},{entry['steps']},{entry['calories']},{entry['distance']},{entry['active_minutes']}\n"

    response = Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=fitness_data.csv"}
    )
    return response


if __name__ == '__main__':
    app.run(debug=True)

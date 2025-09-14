from flask import Flask, render_template, request, redirect, jsonify
import json
import google.generativeai as genai

app = Flask(__name__)
DATA_FILE = 'data.json'

genai.configure(api_key='GEMINI_API_KEY')
model = genai.GenerativeModel('gemini-2.5-flash')


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class FitnessLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None  # Tail pointer for O(1) append operations

    # Logic for Appending the data - O(1) with tail pointer
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    # Logic for Deleting the data
    def delete_by_date(self, date):
        temp = self.head
        prev = None
        while temp:
            if temp.data['date'] == date:
                if prev:
                    prev.next = temp.next
                else:
                    self.head = temp.next
                
                # Update tail pointer if we deleted the last node
                if temp == self.tail:
                    self.tail = prev
                return
            prev = temp
            temp = temp.next

    # Linked list to List of Dictionaries
    def to_list(self):
        result = []
        temp = self.head
        while temp:
            result.append(temp.data)
            temp = temp.next
        return result

    # Logic for Loading data from List of Dictionaries
    def load_from_list(self, data_list):
        self.head = None
        self.tail = None
        for data in data_list:
            self.append(data)

    # Get the last entry - O(1) with tail pointer
    def get_last_entry(self):
        if self.tail:
            return self.tail.data
        return None

    # Get the first entry - O(1)
    def get_first_entry(self):
        if self.head:
            return self.head.data
        return None

    # Check if list is empty - O(1)
    def is_empty(self):
        return self.head is None

    # Get the size of the list - O(n) (could be optimized with size counter)
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

@app.route('/chat')
def chat():
    return render_template('chatbot.html')

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

if __name__ == '__main__':
    app.run(debug=True)


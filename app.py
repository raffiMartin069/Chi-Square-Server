from flask import Flask, request, jsonify
from templates.chaitest import ChiCalculator

app = Flask(__name__)
chi = ChiCalculator()


# Endpoint to receive data
@app.route('/receive-data/', methods=['POST'])
def receive_data():
    retrieve_data = request.get_json()  # Get the data from the request
    chi.data = retrieve_data  # access setter method
    print("Data Extracted:", chi.data_extraction())
    return jsonify({'message': 'Data received successfully'})


# Endpoint to retrieve data
@app.route('/get-data/', methods=['GET'])
def get_data():
    print("Analysis Testing:", chi.chi_square_test())  # Debug purposes
    return chi.send_data()


if __name__ == '__main__':
    app.run(debug=True, port=5000)

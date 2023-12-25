from flask import Flask, request, jsonify
from templates.chaitest import ChiCalculator

app = Flask(__name__)
chi = ChiCalculator()


# Endpoint to receive data
@app.route('/receive-data/', methods=['POST'])
def receive_data():
    try:
        retrieve_data = request.get_json()  # Get the data from the request
        chi.data = retrieve_data  # access setter method

        print("Data Extracted:", chi.data_extraction())
        return jsonify({'message': 'Data received successfully'})
    except RuntimeWarning as e:
        return jsonify({'message': 'Error occurred while receiving data, possible None value was passed. -> Trace log at receive-data endpoint.'})
    except ValueError as e:
        return jsonify({'message': 'Error occurred while receiving data. -> Trace log at receive-data endpoint.'})


# Endpoint to retrieve data
@app.route('/get-data/', methods=['GET'])
def get_data():
    print("Analysis Testing:", chi.chi_square_test())  # Debug purposes
    try:
        return chi.send_data()
    except RuntimeWarning as e:
        return jsonify({'message': 'Error occurred while receiving data, possible None value was passed. -> Trace log at get-data endpoint.'})
    except ValueError as e:
        return jsonify({'message': 'Error occurred while retrieving data. -> Trace log at get-data endpoint.'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)

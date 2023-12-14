from flask import jsonify
from scipy.stats import chi2_contingency


class ChiCalculator:
    def __init__(self, data=None, observable_data=None, alpha_value=None, graph_type=None):
        self._data = data
        self._observable_data = observable_data
        self._alpha_value = alpha_value
        self._graph_type = graph_type

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def observable_data(self):
        return self._observable_data

    @observable_data.setter
    def observable_data(self, observable_data):
        self._observable_data = observable_data

    @property
    def alpha_value(self):
        return self._alpha_value

    @alpha_value.setter
    def alpha_value(self, alpha_value):
        self._alpha_value = alpha_value

    @property
    def graph_type(self):
        return self._graph_type

    @graph_type.setter
    def graph_type(self, graph_type):
        self._graph_type = graph_type

    def data_extraction(self):
        """Extracts the data from the JSON file and stores it in the class variables"""
        self.graph_type = self._data['graph_type']
        self.alpha_value = self._data['degree_of_freedom']
        self.observable_data = self._data['observable_value']

        return (f'Graph: {self.graph_type}, {type(self.graph_type)}'
                f'\nAlpha Value: {self.alpha_value}, {type(float(self.alpha_value))}'
                f'\nObservable Data: {self.observable_data}, {type(self.observable_data)}')

    def chi_square_test(self):
        """Performs the Chi-Square Test of Independence"""
        a_value = self._data['degree_of_freedom']
        o_value = self._data['observable_value']
        contingency_table = o_value
        chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
        return jsonify({'chi_value': chi2_stat, 'p_value': p_value, 'degree_of_freedom': dof, 'expected_value': expected.tolist()})

    def send_data(self):
        return self.chi_square_test()
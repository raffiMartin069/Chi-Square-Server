import base64
import io

import matplotlib
import numpy as np
from PIL import Image
from scipy import stats
from flask import jsonify
from matplotlib import pyplot as plt
from reportlab.pdfgen import canvas
from scipy.stats import chi2_contingency, chi2

matplotlib.use('Agg')


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
        try:
            if self._data:
                """Extracts the data from the JSON file and stores it in the class variables"""
                # self._graph_type = self._data['graph_type']
                self.alpha_value = self._data['degree_of_freedom']
                self.observable_data = self._data['observable_value']

            return (f'\nAlpha Value: {self.alpha_value}, {type(float(self.alpha_value))}'
                    f'\nObservable Data: {self.observable_data}, {type(self.observable_data)}')
        except ValueError:
            return 'Please ensure that the data you have entered is correct -> Trace Log at data_extraction.'

    def chi_square_test(self):
        """Performs the Chi-Square Test of Independence"""
        try:
            # a_value = self._data['degree_of_freedom']
            o_value = self._data['observable_value']
            contingency_table = o_value
            chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
            format_chi2_stat = "{:.3f}".format(float(chi2_stat))
            format_p_value = "{:.3f}".format(float(p_value))
            if float(p_value) < float(self.alpha_value):
                hypothesis_result = 'Reject Null Hypothesis'
            else:
                hypothesis_result = 'Accept Null Hypothesis'
            results = {'chi_value': format_chi2_stat, 'p_value': p_value, 'degree_of_freedom': dof,
                            'expected_value': expected.tolist(),
                            'graph': ChiCalculator.plot_graph(p_value, chi2_stat, self.alpha_value, dof),
                            'hypothesis': hypothesis_result}
            pdf_report = self._generate_report(results)
            results['pdf_report'] = pdf_report
            return jsonify(results)
        except ValueError:
            return jsonify(
                {'message': 'Please ensure that the data you have entered is correct. '
                            '-> Trace Log at chi_square_test.'})

    def _to_decode(self, to_decode):
        # Decode base64 string
        decoded_data = base64.b64decode(to_decode)
        # Create an in-memory Image object from the decoded data
        image = Image.open(io.BytesIO(decoded_data))
        return image

    def _generate_report(self, results):
        try:
            # Create a PDF report
            buffer = io.BytesIO()
            generate_pdf = canvas.Canvas(buffer)
            # Add title
            generate_pdf.setFont('Helvetica', 16)
            generate_pdf.drawString(180, 750, 'Chi-Square Test of Independence')
            # Add results
            generate_pdf.setFont('Helvetica', 12)
            y_position = 700
            for i, j in results.items():
                if i == 'graph':
                    to_decode = j
                    temp = self._to_decode(to_decode)
                    generate_pdf.drawInlineImage(self._to_decode(to_decode), 100, y_position - 220, width=390, height=230)
                    y_position -= 240  # Adjust the vertical position after drawing the graph
                    continue
                if i == 'expected_value':
                    generate_pdf.drawString(100, y_position, f'Expected Value:')
                    y_position -= 20
                    for k in j:
                        generate_pdf.drawString(100, y_position, f'{k}')
                        y_position -= 20
                    continue
                generate_pdf.drawString(100, y_position, f'{i}: {j}')
                y_position -= 20
            # save PDF
            generate_pdf.save()
            buffer.seek(0)
            base64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
            return base64_pdf
        except ValueError:
            return 'Please ensure that the data you have entered is correct -> Trace Log at _generate_report.'

    @staticmethod
    def plot_graph(p_value, chi2_stat, a_value, dof):
        try:
            critical_value = stats.chi2.ppf(1 - float(a_value), float(dof))
            # Check if required parameters are present
            if p_value is None or chi2_stat is None:
                return None
            # Calculate the maximum x-value based on the degree of freedom, critical value, and chi-square statistic
            max_x_value = max(dof + 10, critical_value + 5, chi2_stat + 5)

            # Create a figure and axis
            fig, ax = plt.subplots()
            # Adjust the range of x-values
            x_values = np.linspace(0, max_x_value, 1000)
            y_values = chi2.pdf(x_values, dof)
            # Plot the Chi-Square Distribution
            ax.plot(x_values, y_values, color='blue', label='Chi-Square Distribution')
            # Add a vertical red line at the chi-square statistic
            ax.axvline(x=chi2_stat, color='red', linestyle='--', label=f'X² Statistic: {chi2_stat:.3f}')
            # Shade the rejection region
            rejection_region = np.linspace(chi2_stat, max_x_value, 1000)
            ax.fill_between(rejection_region, chi2.pdf(rejection_region, dof), color='gray', alpha=0.3,
                            label='Rejection Region')
            # Set labels and title dynamically
            ax.set_xlabel('Chi-Square Statistic')
            ax.set_ylabel('Probability Density Function')
            ax.set_title(f'Chi-Square Test of Independence (df={dof})')
            # Show the significance level, critical value, and other relevant information below the rejection region
            info_text = f'Significance Level: {float(a_value):.3f}\nCritical Value: {critical_value:.3f}'
            ax.text(0.1, 0.95, info_text, transform=ax.transAxes, fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
            # Add legend dynamically
            ax.legend()
            # Convert the figure to a base64-encoded string
            image_stream = io.BytesIO()
            fig.savefig(image_stream, format='png')
            image_stream.seek(0)
            base64_image = base64.b64encode(image_stream.read()).decode('utf-8')
            # Close the figure to release resources
            plt.close()
            return base64_image
        except ValueError:
            return 'Please ensure that the data you have entered is correct -> Trace Log at plot_graph.'

    def send_data(self):
        try:
            return self.chi_square_test()
        except ValueError:
            return jsonify({'message': 'Error occurred while retrieving data -> Trace log at send_data endpoint, '
                                       'ChaiCalculator class.'})

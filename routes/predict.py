from flask import Blueprint, send_file
import matplotlib.pyplot as plt
from io import BytesIO

# Create a Blueprint named 'predict_bp'
predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['GET'])
def predict():
    # Sample datapoints for the bar chart
    categories = ['Team A', 'Team B', 'Team C', 'Team D']
    predictions = [0.75, 0.60, 0.85, 0.50]  # Sample prediction scores

    plt.figure(figsize=(8, 6))
    plt.bar(categories, predictions, color='skyblue')
    plt.title('Sample Soccer Match Predictions')
    plt.xlabel('Teams')
    plt.ylabel('Prediction Score')
    plt.ylim(0, 1)

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')
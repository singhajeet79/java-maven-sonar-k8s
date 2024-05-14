from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def extract_data(keyword, number_of_pages, current_date):
    # Placeholder for data extraction logic
    # This should return a DataFrame
    data = {
        'Product Name': [f'{keyword} Product {i}' for i in range(10)],
        'Price': [10 + i for i in range(10)],
        'Date': [current_date for _ in range(10)]
    }
    return pd.DataFrame(data)

@app.route('/')
def search():
    return render_template('search.html')

@app.route('/results', methods=['POST'])
def results():
    keyword = request.form.get('keyword')
    number_of_pages = request.form.get('number_of_pages')
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    name_filter = request.form.get('name_filter')

    if keyword and number_of_pages:
        current_date = datetime.now().strftime("%Y%m%d%H")
        products = extract_data(keyword, int(number_of_pages), current_date)
    else:
        products = pd.read_csv('price_change.csv')
        if min_price:
            products = products[products['Price'] >= float(min_price)]
        if max_price:
            products = products[products['Price'] <= float(max_price)]
        if name_filter:
            products = products[products['Product Name'].str.contains(name_filter, case=False, na=False)]

    return render_template('results.html', tables=[products.to_html(classes='data', header="true")])

if __name__ == '__main__':
    app.run(debug=True)

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def extract_data(keyword, number_of_pages):
    base_url = 'https://www.amazon.com/s?k='
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    product_list = []

    for page in range(1, number_of_pages + 1):
        url = f"{base_url}{keyword}&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('div', {'data-component-type': 's-search-result'})

            for item in results:
                try:
                    # Debugging output for item
                    print("Debugging item:")
                    print(item.prettify())

                    product_name = item.h2.text.strip()
                    product_url = "https://www.amazon.com" + item.h2.a['href']
                    price_whole = item.find('span', 'a-price-whole')
                    price_fraction = item.find('span', 'a-price-fraction')
                    if price_whole and price_fraction:
                        product_price = price_whole.text.strip() + price_fraction.text.strip()
                    else:
                        product_price = 'N/A'
                    product_list.append(
                        {"Product Name": product_name, "Price": product_price, "URL": product_url})
                except AttributeError as e:
                    print(f"AttributeError: {e}")
                    continue

    df = pd.DataFrame(product_list)
    print("Extracted DataFrame:")
    print(df.head())
    return df

def save_to_csv(dataframe, filename):
    dataframe.to_csv(filename, index=False)

def get_price_change(new_data, old_filename='price_change.csv'):
    try:
        old_data = pd.read_csv(old_filename)

        print("Old DataFrame:")
        print(old_data.head())

        # Ensure both dataframes have the 'Product Name' column
        if 'Product Name' not in new_data.columns or 'Product Name' not in old_data.columns:
            print("Error: 'Product Name' column is missing in one of the dataframes.")
            return pd.DataFrame()

        merged_data = new_data.merge(old_data, on='Product Name', suffixes=('_new', '_old'))
        merged_data['Price_new'] = merged_data['Price_new'].replace('N/A', '0').astype(float)
        merged_data['Price_old'] = merged_data['Price_old'].replace('N/A', '0').astype(float)
        merged_data['Price Change'] = merged_data['Price_new'] - merged_data['Price_old']
        price_changes = merged_data[['Product Name', 'Price_new', 'Price_old', 'Price Change', 'URL_new']]
        price_changes.columns = ['Product Name', 'New Price', 'Old Price', 'Price Change', 'URL']
        return price_changes
    except FileNotFoundError:
        print("Old price data not found, saving new data as the initial data.")
        save_to_csv(new_data, old_filename)
        return pd.DataFrame()

if __name__ == '__main__':
    keyword = input("Enter the product keyword to search for: ")
    number_of_pages = int(input("Enter the number of pages to scrape: "))
    current_date = datetime.now().strftime("%Y%m%d%H")
    filename = f'amazon_products_{current_date}.csv'

    products_df = extract_data(keyword, number_of_pages)
    save_to_csv(products_df, filename)

    price_changes_df = get_price_change(products_df)
    if not price_changes_df.empty:
        price_changes_filename = f'price_changes_{current_date}.csv'
        save_to_csv(price_changes_df, price_changes_filename)
        print(f"Price changes saved to {price_changes_filename}")

    print(f"Data saved to {filename}")

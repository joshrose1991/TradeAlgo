import requests
import json
from datetime import datetime, timedelta

print("X")  # Placeholder print statement

api_url = 'https://api.api-ninjas.com/v1/interestrate'

response = requests.get(api_url, headers={'X-Api-Key': 'QB0mPDL+FkEdkKufdBSk5w==VvGlVRWTKr2EogJJ'})

if response.status_code == requests.codes.ok:
    # Parse the JSON response text
    data = json.loads(response.text)
    
    # Extract lists from the parsed data
    central_bank_rates = data.get("central_bank_rates", [])
    non_central_bank_rates = data.get("non_central_bank_rates", [])
    
    # Assign central bank rates to individual variables
    american_rate = None
    australian_rate = None
    brazilian_rate = None
    british_rate = None
    canadian_rate = None
    chilean_rate = None
    chinese_rate = None
    czech_rate = None
    danish_rate = None
    european_rate = None
    hungarian_rate = None
    indian_rate = None
    israeli_rate = None
    japanese_rate = None
    mexican_rate = None
    new_zealand_rate = None
    norwegian_rate = None
    polish_rate = None
    russian_rate = None
    saudi_arabian_rate = None
    south_african_rate = None
    south_korean_rate = None
    swedish_rate = None
    swiss_rate = None
    turkish_rate = None

    for rate in central_bank_rates:
        country = rate['country']
        rate_pct = rate['rate_pct']
        
        if country == "United States":
            american_rate = rate_pct
        elif country == "Australia":
            australian_rate = rate_pct
        elif country == "Brazil":
            brazilian_rate = rate_pct
        elif country == "United Kingdom":
            british_rate = rate_pct
        elif country == "Canada":
            canadian_rate = rate_pct
        elif country == "Chile":
            chilean_rate = rate_pct
        elif country == "China":
            chinese_rate = rate_pct
        elif country == "Czech Republic":
            czech_rate = rate_pct
        elif country == "Denmark":
            danish_rate = rate_pct
        elif country == "Europe":
            european_rate = rate_pct
        elif country == "Hungary":
            hungarian_rate = rate_pct
        elif country == "India":
            indian_rate = rate_pct
        elif country == "Israel":
            israeli_rate = rate_pct
        elif country == "Japan":
            japanese_rate = rate_pct
        elif country == "Mexico":
            mexican_rate = rate_pct
        elif country == "New Zealand":
            new_zealand_rate = rate_pct
        elif country == "Norway":
            norwegian_rate = rate_pct
        elif country == "Poland":
            polish_rate = rate_pct
        elif country == "Russia":
            russian_rate = rate_pct
        elif country == "Saudi Arabia":
            saudi_arabian_rate = rate_pct
        elif country == "South Africa":
            south_african_rate = rate_pct
        elif country == "South Korea":
            south_korean_rate = rate_pct
        elif country == "Sweden":
            swedish_rate = rate_pct
        elif country == "Switzerland":
            swiss_rate = rate_pct
        elif country == "Türkiye" or country == "Turkey":
            turkish_rate = rate_pct

    # Print the central bank rates
    print(f"American Central Bank Rate: {american_rate}%")
    print(f"Australian Central Bank Rate: {australian_rate}%")
    print(f"Brazilian Central Bank Rate: {brazilian_rate}%")
    print(f"British Central Bank Rate: {british_rate}%")
    print(f"Canadian Central Bank Rate: {canadian_rate}%")
    print(f"Chilean Central Bank Rate: {chilean_rate}%")
    print(f"Chinese Central Bank Rate: {chinese_rate}%")
    print(f"Czech Central Bank Rate: {czech_rate}%")
    print(f"Danish Central Bank Rate: {danish_rate}%")
    print(f"European Central Bank Rate: {european_rate}%")
    print(f"Hungarian Central Bank Rate: {hungarian_rate}%")
    print(f"Indian Central Bank Rate: {indian_rate}%")
    print(f"Israeli Central Bank Rate: {israeli_rate}%")
    print(f"Japanese Central Bank Rate: {japanese_rate}%")
    print(f"Mexican Central Bank Rate: {mexican_rate}%")
    print(f"New Zealand Central Bank Rate: {new_zealand_rate}%")
    print(f"Norwegian Central Bank Rate: {norwegian_rate}%")
    print(f"Polish Central Bank Rate: {polish_rate}%")
    print(f"Russian Central Bank Rate: {russian_rate}%")
    print(f"Saudi Arabian Central Bank Rate: {saudi_arabian_rate}%")
    print(f"South African Central Bank Rate: {south_african_rate}%")
    print(f"South Korean Central Bank Rate: {south_korean_rate}%")
    print(f"Swedish Central Bank Rate: {swedish_rate}%")
    print(f"Swiss Central Bank Rate: {swiss_rate}%")
    print(f"Turkish Central Bank Rate: {turkish_rate}%")

    # Print the non-central bank rates
    print("\nNon-Central Bank Rates:")
    for rate in non_central_bank_rates:
        print(rate)
else:
    print("Error:", response.status_code, response.text)

api_url = 'https://api.api-ninjas.com/v1/interestratehistorical'
api_key = 'QB0mPDL+FkEdkKufdBSk5w==VvGlVRWTKr2EogJJ'

# Define the date range for the last year

# Define the current date and one year ago in Unix timestamp format
current_time = datetime.now()
one_year_ago = current_time - timedelta(days=365)
one_year_ago_unix = int(one_year_ago.timestamp())

# List of countries to query
countries = ["United States", "Australia", "Brazil", "United Kingdom", "Canada", 
             "Chile", "China", "Czech Republic", "Denmark", "Europe", "Hungary", 
             "India", "Israel", "Japan", "Mexico", "New Zealand", "Norway", 
             "Poland", "Russia", "Saudi Arabia", "South Africa", "South Korea", 
             "Sweden", "Switzerland", "Türkiye"]

# Function to fetch historical interest rates for a country
def fetch_historical_rates(country):
    params = {
        'country': country,
        'start_date': one_year_ago_unix,
        'end_date': int(current_time.timestamp())
    }
    response = requests.get(api_url, headers={'X-Api-Key': api_key}, params=params)
    if response.status_code == requests.codes.ok:
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response for {country}: {e}")
            return None
    else:
        print(f"Error fetching data for {country}: {response.status_code}")
        return None

# Fetch and print historical interest rates for all countries
historical_rates = {}

for country in countries:
    print(f"Fetching data for {country}...")
    rates_response = fetch_historical_rates(country)
    if rates_response:
        if 'data' in rates_response:
            rates = rates_response['data']
            # Filter rates to only include those within the last year based on Unix timestamp
            filtered_rates = [
                rate for rate in rates if rate['timestamp'] >= one_year_ago_unix
            ]
            historical_rates[country] = filtered_rates
        else:
            print(f"Unexpected data format for {country}: {rates_response}")
    else:
        print(f"No data found for {country}.")

# Optionally, print or process the filtered data
for country, rates in historical_rates.items():
    print(f"\nHistorical rates for {country}:")
    for rate in rates:
        if isinstance(rate, dict):
            # Convert the Unix timestamp back to a readable date format
            rate_date = datetime.utcfromtimestamp(rate['timestamp']).strftime('%Y-%m-%d')
            print(f"Date: {rate_date}, Rate: {rate['rate_pct']}%")
        else:
            print(f"Unexpected rate format for {country}: {rate}")

# Now historical_rates dictionary contains all the filtered data for further processing
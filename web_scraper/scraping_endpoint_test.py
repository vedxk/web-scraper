import requests

# Define the URL of your FastAPI server
url = 'http://localhost:8000/scrape' 

headers = {
    "Authorization": "gAAAAABgjTUXB8FVWFlRx-fSKOhS1cU0_KXfCmABaU8kO5opKnXz1ZPV7QXcSAKrFGxq5A5It4gEzfj4gT8XFYFJ_xrAo8JdYg==",
    "Content-Type": "application/json"
}
start_page = int(input("Enter the start page: "))
end_page = int(input("Enter the end page: "))
proxy = str(input("Enter proxy: "))
# Example payload for the /scrape endpoint
payload = {
    'start_page': start_page,
    'end_page': end_page,
    'proxy': proxy 
}

# Send a POST request to the /scrape endpoint
response = requests.post(url, headers=headers, json=payload)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("Scraping successful!")
else:
    print(f"Failed to scrape data. Status code: {response.status_code}")
    print(response.text)

import requests

# URL of the CSS file
css_url = "https://fonts.googleapis.com/css?family=Lato:400,700"

# Send a GET request to fetch the CSS file
response = requests.get(css_url)

# Check if the request was successful
if response.status_code == 200:
    # Save the CSS content to a file
    with open("all.min.css", "w", encoding="utf-8") as file:
        file.write(response.text)
    print("CSS file downloaded and saved as 'all.min.css'")
else:
    print(f"Failed to fetch the CSS file. Status Code: {response.status_code}")

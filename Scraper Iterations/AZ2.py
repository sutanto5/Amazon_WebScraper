#following -> https://oxylabs.io/blog/how-to-scrape-amazon-product-data
'''

#imports
import requests
from bs4 import BeautifulSoup

custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Accept-Language': 'da, en-gb, en',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

#instantiate site
url = 'https://www.amazon.com/Elon-Musk-Walter-Isaacson/dp/1982181281'
response = requests.get(url)

#print(response.text)
print(response.status_code) #200 - success, 503 - error

#getting the page
with open("amazon_page.html", "w") as f:
    f.write(response.text)

response = requests.get(url, headers=custom_headers)
soup = BeautifulSoup(response.text, 'lxml')


#scraping the title
title_element = soup.select_one('#title')
title = title_element.text

print(title)

#scraping the rating
#acrPopover
rating_element = soup.select_one('#acrPopover')
rating_text = rating_element.attrs.get('#averageCustomerReviews')
print(rating_text)

'''

#imports
import requests
from bs4 import BeautifulSoup

custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Accept-Language': 'da, en-gb, en',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

# Instantiate site with custom headers
url = 'https://www.amazon.com/Elon-Musk-Walter-Isaacson/dp/1982181281'
response = requests.get(url, headers=custom_headers)

print(response.status_code)  # 200 means success

# Save the page (optional)
with open("amazon_page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

# Parse the page with BeautifulSoup
soup = BeautifulSoup(response.text, 'lxml')

# Extract Title
title_element = soup.select_one('#title')
title = title_element.get_text(strip=True) if title_element else "Title not found"

# Extract all elements with class "a-size-base a-color-base"
all_spans = soup.find_all('span', class_='a-size-base a-color-base')

# Find the correct span that contains the rating -> Doesn't work
rating = "Rating not found"
rating_container = soup.select_one('#averageCustomerReviews')

if rating_container:
    rating_element = rating_container.find('span', class_='a-size-base a-color-base')
    if rating_element:
        rating = rating_element.get_text(strip=True)

# Scrape Price
price_element = soup.select_one('span.a-offscreen')
price = price_element.text


# Print results
print("Title:", title)
print("Rating:", rating)
print("Price: ", price)



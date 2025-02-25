import requests
from bs4 import BeautifulSoup
import pandas as pd

# Review file
test_asin = "B098FKXT8L"  # Example non-book ASIN
hillbilly_asin = "B08WM3LMJF"  # Example book ASIN

# Given headers
custom_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/135.0"
}

# Function to make request and return BeautifulSoup instance
def get_soup(url):
    response = requests.get(url, headers=custom_headers)
    
    if response.status_code != 200:
        print(f"Error fetching page: {response.status_code}")
        exit(-1)

    return BeautifulSoup(response.text, "lxml")

# Function to get all reviews from the page
def get_reviews(soup, is_book=False):
    reviews = []
    
    # Different review selectors for books vs regular products
    review_selector = "#customer_review-R*" if is_book else "#cm-cr-dp-review-list > li"
    
    # Get the correct review elements
    review_elements = soup.select(review_selector)
    
    for review in review_elements:
        reviews.append(extract_review(review, is_book=is_book))

    return reviews

# Function to extract review details
def extract_review(review, is_book=False):
    author = review.select_one(".a-profile-name").text.strip() if review.select_one(".a-profile-name") else "Unknown"

    # Rating: Adjust for books
    rating_element = review.select_one(".review-rating > span")
    if not rating_element and is_book:
        rating_element = review.select_one(".a-icon-alt")  # Books sometimes store ratings here
    
    rating = rating_element.text.replace("out of 5 stars", "").strip() if rating_element else "No rating"

    date = review.select_one(".review-date").text.strip() if review.select_one(".review-date") else "No date"

    # Different title structure for books
    if is_book:
        title_element = review.select_one(".review-title")
    else:
        title_element = review.select_one(".review-title > span:not([class])")
    
    title = title_element.text.strip() if title_element else "No title"

    # Content (Books often use '.review-text-content' instead of '.review-text')
    content_element = review.select_one(".review-text-content") if is_book else review.select_one(".review-text")
    content = " ".join(content_element.stripped_strings) if content_element else "No content"

    verified_element = review.select_one("span.a-size-mini")
    verified = verified_element.text.strip() if verified_element else None

    # Image handling
    img_selector = ".review-image-tile" if not is_book else ".linkless-review-image-tile"
    image_elements = review.select(img_selector)
    images = [img.attrs["data-src"] for img in image_elements] if image_elements else None

    return {
        "type": "book" if is_book else "product",
        "author": author,
        "rating": rating,
        "title": title,
        "content": content.replace("Read more", ""),
        "date": date,
        "verified": verified,
        "images": images
    }

# Main function to fetch and save reviews
def main():
    asin = "0062300547"  # Change ASIN here
    search_url = f"https://www.amazon.com/Hillbilly-Elegy-Memoir-Family-Culture/product-reviews/0062300547/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&claim_type=EmailAddress&new_account=1&"

    soup = get_soup(search_url)
    
    # Determine if it's a book based on page structure
    is_book = bool(soup.select_one("#booksTitle"))

    reviews = get_reviews(soup, is_book=is_book)
    
    df = pd.DataFrame(reviews)
    df.to_csv(f"reviews_{asin}.csv", index=False)
    print(f"Saved {len(reviews)} reviews to reviews_{asin}.csv")

if __name__ == "__main__":
    main()

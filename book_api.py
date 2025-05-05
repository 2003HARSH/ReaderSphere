import requests

query = "john elia"
url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
response = requests.get(url)
data = response.json()

for book in data['items'][:1]:
    info = book['volumeInfo']
    print("Title:", info.get("title"))
    print("Authors:", info.get("authors"))
    print("Publisher:", info.get("publisher"))
    print("Category:", info.get("categories"))
    print("pageCount:", info.get("pageCount"))
    print("Description:", info.get("description"))
    print("Thumbnail:", info.get("imageLinks", {}).get("thumbnail"))
    print()

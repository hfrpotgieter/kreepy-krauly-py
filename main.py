from search import google_search

for it in google_search("instagram"):
    print(it["title"])
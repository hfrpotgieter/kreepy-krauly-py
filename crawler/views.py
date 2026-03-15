from django.http import HttpResponse
from django.shortcuts import render
import requests
from crawl import crawl_site
from search import web_search
from dataframe import to_dataframe

def home(request):
    return render(request, 'home.html')

import csv
import pandas as pd
from django.http import HttpResponse

def waiting_room(request):
    term = request.GET.get("searchTerm", "")
    search_results = web_search(term)

    contacts = []
    for it in search_results:
        contact = crawl_site(it["link"])
        # Ensure crawl_site didn't return None/Error before appending
        if contact:
            contacts.append(contact)

    # 1. Use the correct variable (contacts)
    df = pd.DataFrame(contacts) 

    # 2. Set up Response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result.csv"'

    # 3. Write DataFrame to the response
    # This avoids manual csv.writer loops
    df.to_csv(path_or_buf=response, index=False)

    return response
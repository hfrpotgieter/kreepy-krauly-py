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
    agent = request.META.get('HTTP_USER_AGENT')
    term = request.GET.get("searchTerm", "")
    contacts = []
    if term.startswith("https") or term.startswith("http"):
        contact = crawl_site(term, agent)
        if contact is not None:
            contacts.append(contact)
    else:
        search_results = web_search(term, agent)
        for it in search_results:
            contact = crawl_site(it["link"], agent)
            if contact is None:
                continue
            contacts.append(contact)


    df = pd.DataFrame(contacts) 

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response
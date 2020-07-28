from django.shortcuts import render
from django.core.cache import caches, cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView
import requests
from requests import PreparedRequest
import time
from ratelimit.decorators import ratelimit
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from stackoverflow import settings

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
CACHE_TTL = getattr(settings, 'CACHE_TTL', 100)

@method_decorator(ratelimit(key='get:search', rate='5/m', method='GET'), name='get')
@method_decorator(ratelimit(key='get:search', rate='100/d', method='GET'), name='get')
@method_decorator(cache_page(60 * 5), name='dispatch')
class Search(ListView):
    paginate_by = 5
    def get(self, request):
        if 'search' in request.GET:
            try:
                search = request.GET['search']
                url = 'https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&site=stackoverflow'
                params = dict(item.split("=") for item in search.split(","))
                req = PreparedRequest()
                req.prepare_url(url, params)
                stackoverflow_url = req.url
                response = requests.get(stackoverflow_url)
                data = response.json()
                if data:
                    length = len(data['items'])
                    relevant_data_to_display = {}
                    for i in range(length):
                        data1 = {}
                        for key, value in data.items():
                            data1['tags'] = data['items'][i]['tags']
                            data1['title'] = data['items'][i]['title']
                            data1['owner_link'] = data['items'][i]['owner']['link']
                            data1['link'] = data['items'][i]['link']
                            question_date = time.strftime('%Y-%m-%d %H:%M:%S',
                                                          time.localtime(data['items'][i]['creation_date']))
                            data1['display_name'] = data['items'][i]['owner']['display_name']
                            data1['creation_date'] = question_date
                        relevant_data_to_display.update({i: data1})
                    dict_to_tuple = list(relevant_data_to_display.items())
                    paginator = Paginator(dict_to_tuple, 5)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    try:
                        dict_to_tuple= paginator.page(page_number)
                    except PageNotAnInteger:
                        dict_to_tuple = paginator.page(1)
                    except EmptyPage:
                        dict_to_tuple = paginator.page(paginator.num_page)
                    return render(request, 'stackoverflow.html', {'data':dict_to_tuple})

            except (KeyError,ValueError,AssertionError,AttributeError) as e:
                return render(request, 'exception.html', {
                })
        return render(request, 'home.html', {
        })



class Home(ListView):
    def get(self,request):
        return render(request,'home.html',{})
from django.shortcuts import render
from django.http import HttpResponse



# A Request handler

#First page
def home (request):
    #In here, you can pull data, transform data, etc
    return render(request, )
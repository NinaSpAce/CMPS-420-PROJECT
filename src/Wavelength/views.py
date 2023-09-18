from django.shortcuts import render

#First page
def home (request):
    #In here, you can pull data, transform data, etc
    return render(request,"pages/home.html", {}) 
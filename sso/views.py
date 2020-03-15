from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
@login_required
def index_view(request):
    contexto = {'user': request.user}
    return render(request, 'sso/index.html', context=contexto)
# Create your views here.

def login_view(request):
    contexto = None
    if(request.user.is_authenticated):
        return redirect('index')
    else:
        return render(request, 'sso/login.html',context = contexto)
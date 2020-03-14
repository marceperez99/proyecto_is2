from django.shortcuts import render
from django.contrib.auth.decorators import login_required
@login_required
def index_view(request):
    contexto = {'user': request.user}
    return render(request, 'sso/index.html', context=contexto)
# Create your views here.


from django.shortcuts import render
@login_required
def index_view(request):
    contexto = {'user': request.user}
    return render(request, 'sso/login.html', context=contexto)
# Create your views here.


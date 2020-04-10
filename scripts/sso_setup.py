from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

SECRET_KEY = 'sw2lVjRDgG1GtDAZVC_QmVhr'
CLIENT_ID = '347886323853-r72mjg1utuabev2f73ngef3tg2nqluth.apps.googleusercontent.com'
s = Site.objects.get(domain='example.com')
s.domain = 'localhost:8000'
s.name = 'localhost'
s.save()
sa = SocialApp(provider='google', name='gapi', client_id=CLIENT_ID, secret=SECRET_KEY)
sa.save()
sa.sites.set([s])

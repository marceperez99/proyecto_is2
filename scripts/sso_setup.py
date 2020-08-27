from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.conf import settings

SECRET_KEY = settings.GOOGLE_OAUTH_SECRET_KEY
CLIENT_ID = settings.GOOGLE_OAUTH_CLIENT_ID
print("Secret Key", SECRET_KEY)
print("Cliend ID", CLIENT_ID)


if not SocialApp.objects.filter(name='gapi').exists():
    s = Site.objects.get(domain='example.com')
    s.domain = settings.SOCIALAPP_DOMAIN
    s.name = settings.SOCIALAPP_NAME
    s.save()
    sa = SocialApp(provider='google', name='gapi', client_id=CLIENT_ID, secret=SECRET_KEY)
    sa.save()
    print("im in")
    sa.sites.set([s])
else:
    print("Algo paso")

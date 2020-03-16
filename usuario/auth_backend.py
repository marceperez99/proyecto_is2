from django.contrib.auth.backends import ModelBackend

class ProxiedModelBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
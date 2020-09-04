from django.contrib.auth.models import User, Group


def user_factory(username, password, email, rol_de_sistema):
    """
    Factory que retorna un objeto User
    :param username:
    :param password:
    :param email:
    :return: User
    """
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    rol = Group.objects.get(name=rol_de_sistema)
    user.groups.add(rol)
    return user
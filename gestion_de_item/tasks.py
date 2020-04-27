from celery import shared_task


@shared_task
def tarea():
    print("Hola soy una tarea asincrona")

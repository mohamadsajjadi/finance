from celery import shared_task


@shared_task
def create_object(serializer, store):
    serializer.save(store)

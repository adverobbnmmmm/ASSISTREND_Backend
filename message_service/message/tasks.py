#cleanup tasks for celery worker

from celery import shared_task
from .models import OneToOneMessage,GroupMessage

@shared_task
def cleanup_one_to_one_messages():
    deleted, _ = OneToOneMessage.objects.filter(sent_to_receiver=True).delete()
    return f"Deleted {deleted} one-to-one messages."

@shared_task
def cleanup_group_messages():
    deleted_count = 0
    # Loop through each group message in the database
    for msg in GroupMessage.objects.select_related('group').all():
        # Get total number of members in the group this message belongs to
        total_group_members = msg.group.members.count()

        # Get number of users who have received this particular message
        delivered_count = msg.delivered_to.count()

        # If everyone in the group has received this message
        if delivered_count == total_group_members:
            msg.delete()  # Safe to delete this message
            deleted_count += 1

    return f"Deleted {deleted_count} group messages."
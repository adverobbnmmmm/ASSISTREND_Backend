import time
from django.core.management.base import BaseCommand
from django.conf import settings
from elasticsearch import Elasticsearch
class Command(BaseCommand):
"""Django command to wait for Elasticsearch to be available"""
    def handle(self, *args, **options):
        self.stdout.write('Waiting for Elasticsearch…')
        Es_host = settings.ELASTICSEARCH_DSL['default']['hosts']
        Es_up = False
        while not es_up:
        try:
            Es = Elasticsearch([es_host])
            Es.cluster.health(wait_for_status="yellow", request_timeout=1)
            Es_up = True
        except Exception:
            self.stdout.write('Elasticsearch unavailable, waiting…')
            Time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Elasticsearch available!'))
from django.core.management import BaseCommand
import sys
sys.path.append(".")
from base.views import cache_popular_tags


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache_popular_tags()

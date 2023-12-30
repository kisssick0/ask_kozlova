from django.core.management import BaseCommand
import sys
sys.path.append(".")
from base.views import cache_best_members


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache_best_members()

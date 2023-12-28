import random

from django.core.management import BaseCommand
from faker import Faker
import sys
sys.path.append(".")

from base.models import Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile, QuestionTag
from django.contrib.auth.models import User


entities = [Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile, User]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for e in entities:
            e.objects.all().delete()

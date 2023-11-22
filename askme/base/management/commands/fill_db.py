import random

from django.core.management import BaseCommand
from faker import Faker
import sys
sys.path.append(".")

from base.models import Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile, QuestionTag
from django.contrib.auth.models import User

fake = Faker()

entities = [Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile, User]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **kwargs):
        for e in entities:
            e.objects.all().delete()

        ratio = kwargs['ratio']

        users = [
            User(
                username=fake.unique.user_name(),
                email=fake.email()
            ) for _ in range(ratio)
        ]
        User.objects.bulk_create(users)

        profiles = [
            Profile(
                user=user,
                login=user.username,
                nickname=fake.unique.user_name()
            ) for user in users
        ]
        Profile.objects.bulk_create(profiles)

        tags = [
            Tag(
                tag_name=fake.unique.bothify(text='tag_????')
            ) for _ in range(ratio)
        ]
        Tag.objects.bulk_create(tags)
        tag_ids = list(Tag.objects.values_list('id', flat=True))

        questions = [
            Question(
                user=random.choice(profiles),
                title=fake.text(max_nb_chars=40),
                content=fake.text(max_nb_chars=255),
                date_add=str(fake.date_between(start_date='-5y', end_date='-1d'))
            ) for _ in range(ratio * 10)
        ]
        Question.objects.bulk_create(questions)
        question_ids = list(Question.objects.values_list('id', flat=True))

        tags_to_question = []
        for q_id in question_ids:
            q_tags = []
            for i in range(0, random.randint(1, 3)):
                tag_id = tag_ids[random.randint(0, len(tag_ids) - 1)]
                if tag_id not in q_tags:
                    q_tags.append(tag_id)
            for tag in q_tags:
                tags_to_question.append(QuestionTag(question=Question.objects.get(pk=q_id), tag=Tag.objects.get(pk=tag)))
        QuestionTag.objects.bulk_create(tags_to_question)

        answers = [
            Answer(
                question=random.choice(questions),
                user=random.choice(profiles),
                content=fake.text(max_nb_chars=255),
                status=fake.boolean(chance_of_getting_true=50)
            ) for _ in range(ratio * 100)
        ]
        Answer.objects.bulk_create(answers)

        answer_likes = [
            LikeAnswer(
                answer=random.choice(answers),
                like=random.choice([-1, 1]),
                user=random.choice(profiles)
            ) for _ in range(ratio * 100)
        ]
        LikeAnswer.objects.bulk_create(answer_likes)

        question_likes = [
            LikeQuestion(
                question=random.choice(questions),
                like=random.choice([-1, 1]),
                user=random.choice(profiles)
            ) for _ in range(ratio * 100)
        ]
        LikeQuestion.objects.bulk_create(question_likes)

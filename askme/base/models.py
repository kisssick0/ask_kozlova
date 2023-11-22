from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch, Sum, Max
from django.core.validators import MaxValueValidator, MinValueValidator


class QuestionManager(models.Manager):
    def sort_by_latest(self, count=100):
        questions = Question.objects.order_by('-date_add')[:count]
        questions_ids = [question.pk for question in questions]
        likes = LikeQuestion.manager.likes_on_question_value(questions_ids)
        items = []
        for question in questions:
            question_id = question.pk
            likes_count = likes[question_id]
            question_tag_ids = QuestionTag.objects.filter(question=question_id)
            tags = [Tag.objects.get(pk=qt.tag_id) for qt in question_tag_ids]
            items.append([question]
                         + [tags]
                         + [Answer.manager.count_answers_on_question(question_id)]
                         + [likes_count]
                         )
        return items

    def question_by_id(self, question_id):
        question = Question.objects.get(pk=question_id)
        question_tag_id = QuestionTag.objects.filter(question=question_id)
        tags = [Tag.objects.get(pk=qt.tag_id) for qt in question_tag_id]
        likes = LikeQuestion.manager.likes_on_question_value([question.pk])
        question = [question] + [tags] + [Answer.manager.count_answers_on_question(question.pk)] + [likes[question_id]]
        return question

    def filter_by_tag(self, tag_name: str):
        tag = Tag.objects.get(tag_name=tag_name)
        question_tag_ids = QuestionTag.objects.filter(tag=tag.pk)
        questions = [Question.objects.get(pk=qt.question_id) for qt in question_tag_ids]
        items = []
        for question in questions:
            question_tag_ids = QuestionTag.objects.filter(question=question.pk)
            tags = [Tag.objects.get(pk=qt.tag_id) for qt in question_tag_ids]
            likes = LikeQuestion.manager.likes_on_question_value([question.pk])
            items.append([question]
                         + [tags]
                         + [Answer.manager.count_answers_on_question(question.pk)]
                         + [likes[question.pk]]
                         )
        return items

    def sort_by_hot(self):
        queryset = LikeQuestion.manager.max_likes_on_questions()
        question_ids = [qs['question'] for qs in queryset]
        likes = [qs['sumlikes'] for qs in queryset]
        questions = Question.objects.filter(pk__in=question_ids)
        question_tag_ids = QuestionTag.objects.filter(question__in=question_ids)
        tags = [Tag.objects.get(pk=qt.tag_id) for qt in question_tag_ids]
        items = []
        for i in range(len(questions)):
            items.append([questions[i]] + [[tags[i]]] + [Answer.manager.count_answers_on_question(question_ids[i])] + [likes[i]])
        return items


class AnswerManager(models.Manager):
    def answers_on_question(self, question_id: int):
        answers = Answer.objects.filter(question=question_id).order_by('-status')
        answers_ids = [answer.pk for answer in answers]
        likes = LikeAnswer.manager.likes_on_answer_value(answers_ids)
        items = []
        for like in likes:
            items.append([answers.get(pk=like[0])] + [like[1]])
        return items

    def count_answers_on_question(self, question_id: int):
        return Answer.objects.filter(question=question_id).count()


class TagManager(models.Manager):
    def popular_tags(self):
        queryset = QuestionTag.objects.values('tag').annotate(count_q=Count('question')).order_by('-count_q')[:10]
        tags = Tag.objects.filter(pk__in=[el['tag'] for el in queryset])
        return tags


class ProfileManager(models.Manager):
    def best_members(self):
        # больше всего правильных ответов
        queryset = Answer.objects.filter(status=True).values('user').annotate(count=Count('status')).order_by('-count')[:10]
        user_ids = [qs['user'] for qs in queryset]
        best_members = Profile.objects.filter(pk__in=user_ids)
        nicknames = [member.nickname for member in best_members]
        return nicknames


class LikeQuestionManager(models.Manager):
    def likes_on_question_value(self, question_ids):
        likes = LikeQuestion.objects.filter(question__in=question_ids)
        question_likes_ids = [like.question.pk for like in likes]
        items = {}
        for question_id in question_ids:
            if question_id in question_likes_ids:
                items[question_id] = likes.filter(question=question_id).aggregate(sum_likes=Sum('like'))['sum_likes']
            else:
                items[question_id] = 0
        return items

    def max_likes_on_questions(self, count=100):
        items = LikeQuestion.objects.values('question').annotate(sumlikes=Sum('like')).order_by('-sumlikes')[:count]
        return items


class LikeAnswerManager(models.Manager):
    def likes_on_answer_value(self, answer_ids):
        likes = LikeAnswer.objects.filter(answer__in=answer_ids)
        answer_likes_ids = [like.answer.pk for like in likes]
        items = []
        for answer_id in answer_ids:
            if answer_id in answer_likes_ids:
                items.append([answer_id]
                             + [likes.filter(answer=answer_id).aggregate(sum_likes=Sum('like'))['sum_likes']]
                             )
            else:
                items.append([answer_id] + [0])
        return items


class Question(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_add = models.DateTimeField()

    objects = models.Manager()
    manager = QuestionManager()

    class Meta:
        default_related_name = 'questions'

    def __str__(self):
        return f"{self.user} {self.title}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=255)
    login = models.CharField(max_length=255)
    #avatar = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f"{self.nickname}"

    objects = models.Manager()
    manager = ProfileManager()


class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    content = models.TextField()

    STATUS_CHOICES = (
        (True, 'Correct'),
        (False, 'Incorrect')
    )

    status = models.BooleanField(choices=STATUS_CHOICES, default=False)

    objects = models.Manager()
    manager = AnswerManager()

    def __str__(self):
        return f"Answer {self.user}"


class Tag(models.Model):
    tag_name = models.CharField(max_length=255, default='all')

    objects = models.Manager()
    manager = TagManager()

    class Meta:
        default_related_name = 'tags'

    def __str__(self):
        return f"{self.tag_name}"


class LikeQuestion(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    like = models.IntegerField(default=0, validators=[MaxValueValidator(1), MinValueValidator(-1)])
    user = models.ForeignKey('Profile', on_delete=models.DO_NOTHING)

    objects = models.Manager()
    manager = LikeQuestionManager()

    def __str__(self):
        return f"{self.user} : {self.like}"


class LikeAnswer(models.Model):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    like = models.IntegerField(default=0, validators=[MaxValueValidator(1), MinValueValidator(-1)])
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)

    objects = models.Manager()
    manager = LikeAnswerManager()

    def __str__(self):
        return f"{self.user} : {self.like}"


class QuestionTag(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)

    objects = models.Manager()

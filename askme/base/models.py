from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch, Sum, Max
from django.core.validators import MaxValueValidator, MinValueValidator


class QuestionManager(models.Manager):
    def sort_by_latest(self, count=100):
        questions = Question.objects.order_by('-date_add')[:count]
        questions_ids = [question.pk for question in questions]
        likes = LikeQuestion.manager.likes_on_question_value(questions_ids)
        question_tag_ids = QuestionTag.objects.filter(question__in=questions_ids)
        tags = Tag.objects.filter(pk__in=question_tag_ids.values_list('tag_id', flat=True))
        answer_counts = Answer.manager.count_answers_on_questions(questions_ids)
        items = []
        for question in questions:
            question_id = question.pk
            try:
                likes_count = likes.get(question=question_id)['sum_likes']
            except:
                likes_count = 0
            question_tags = tags.filter(pk__in=question_tag_ids.filter(question=question_id).values('tag_id'))
            try:
                answer_count = answer_counts.get(question=question_id)
            except:
                answer_count = {'count_answers': 0}
            items.append([question]
                         + [question_tags]
                         + [answer_count['count_answers']]
                         + [likes_count]
                         )
        return items

    def question_by_id(self, question_id: int):
        question = Question.objects.get(pk=question_id)
        question_tag_ids = QuestionTag.objects.filter(question=question_id)
        tags = [Tag.objects.get(pk=qt.tag_id) for qt in question_tag_ids]
        try:
            likes = LikeQuestion.manager.likes_on_question_value([question.pk]).get(question=question_id)['sum_likes']
        except:
            likes = 0
        items = [question] + [tags] + [Answer.manager.count_answers_on_question(question.pk)] + [likes]
        return items

    def filter_by_tag(self, tag_name: str):
        tag = Tag.objects.get(tag_name=tag_name)
        question_tag_ids = QuestionTag.objects.filter(tag=tag.pk)
        questions = [Question.objects.get(pk=qt.question_id) for qt in question_tag_ids]
        items = []
        for question in questions:
            question_tag_ids = QuestionTag.objects.filter(question=question.pk)
            tags = [Tag.objects.get(pk=qt.tag_id) for qt in question_tag_ids]
            try:
                likes = LikeQuestion.manager.likes_on_question_value([question.pk])[0]['sum_likes']
            except:
                likes = 0
            items.append([question]
                         + [tags]
                         + [Answer.manager.count_answers_on_question(question.pk)]
                         + [likes]
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
            items.append(
                [questions[i]] + [[tags[i]]] + [Answer.manager.count_answers_on_question(question_ids[i])] + [likes[i]])
        return items


class AnswerManager(models.Manager):
    def answers_on_question(self, question_id: int):
        answers = Answer.objects.filter(question=question_id).order_by('-status')
        answers_ids = [answer.pk for answer in answers]
        likes = LikeAnswer.manager.likes_on_answer_value(answers_ids)
        likes_answers_ids = [answer['answer'] for answer in likes.filter(answer__in=answers_ids).values('answer')]
        items = []
        for answer in answers:
            items.append(
                [answer] +
                [0 if answer.pk not in likes_answers_ids
                 else likes.get(answer=answer.pk)['sum_likes']]
            )
        return items

    def count_answers_on_question(self, question_id: int):
        return Answer.objects.filter(question=question_id).count()

    def count_answers_on_questions(self, question_ids: list):
        return Answer.objects.filter(question__in=question_ids).values('question').annotate(count_answers=Count('question'))


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
        best_members = Profile.objects.filter(pk__in=user_ids).values('user_id')
        nicknames = User.objects.filter(pk__in=best_members)
        return nicknames


class LikeQuestionManager(models.Manager):
    def likes_on_question_value(self, question_ids: list):
        likes = LikeQuestion.objects.filter(question__in=question_ids)
        items = likes.values('question').annotate(sum_likes=Sum('like'))
        return items

    def max_likes_on_questions(self, count=100):
        items = LikeQuestion.objects.values('question').annotate(sumlikes=Sum('like')).order_by('-sumlikes')[:count]
        return items


class LikeAnswerManager(models.Manager):
    def likes_on_answer_value(self, answer_ids: list):
        likes = LikeAnswer.objects.filter(answer__in=answer_ids).values('answer').annotate(sum_likes=Sum('like'))
        return likes


class Question(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='user_question')
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_add = models.DateTimeField()

    objects = models.Manager()
    manager = QuestionManager()

    class Meta:
        default_related_name = 'question'

    def __str__(self):
        return f"{self.user} {self.title}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=255)
    # avatar = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f"{User.username}"

    objects = models.Manager()
    manager = ProfileManager()


class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='question_answer')
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='user_answer')
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
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='question_likes')
    like = models.IntegerField(default=0, validators=[MaxValueValidator(1), MinValueValidator(-1)])
    user = models.ForeignKey('Profile', on_delete=models.DO_NOTHING, related_name='user_like_question')

    objects = models.Manager()
    manager = LikeQuestionManager()

    def __str__(self):
        return f"{self.user} : {self.like}"


class LikeAnswer(models.Model):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, related_name='answer_likes')
    like = models.IntegerField(default=0, validators=[MaxValueValidator(1), MinValueValidator(-1)])
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='user_like_answer')

    objects = models.Manager()
    manager = LikeAnswerManager()

    def __str__(self):
        return f"{self.user} : {self.like}"


class QuestionTag(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='question_tag')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='tags_for_questions')

    objects = models.Manager()

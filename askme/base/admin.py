from django.contrib import admin

# Register your models here.
from . models import Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile, QuestionTag

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(LikeQuestion)
admin.site.register(LikeAnswer)
admin.site.register(Profile)
admin.site.register(QuestionTag)

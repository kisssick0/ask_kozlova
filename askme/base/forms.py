import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime

from . models import Profile, Question, Tag, QuestionTag, Answer


class LoginForm(forms.Form):
    username = forms.CharField(min_length=5,
                               max_length=50,
                               widget=forms.TextInput(attrs={"class": "input-control"}),
                               required=True
                               )
    password = forms.CharField(min_length=4,
                               max_length=50,
                               widget=forms.PasswordInput(attrs={"class": "input-control"}),
                               required=True
                               )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username__exact=username).exists():
            raise ValidationError('No such username')
        return username


class RegisterForm(forms.ModelForm):
    nickname = forms.CharField(min_length=5,
                               max_length=50,
                               widget=forms.TextInput(attrs={"class": "input-control"}),
                               required=True
                               )
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "input-control"}),
                            required=True
                            )
    username = forms.CharField(min_length=5,
                               max_length=50,
                               widget=forms.TextInput(attrs={"class": "input-control"}),
                               required=True
                               )
    password = forms.CharField(min_length=4,
                               max_length=50,
                               widget=forms.PasswordInput(attrs={"class": "input-control"}),
                               required=True
                               )
    password_check = forms.CharField(min_length=4,
                                     max_length=50,
                                     widget=forms.PasswordInput(attrs={"class": "input-control"})
                                     )

    class Meta:
        model = User
        fields = ['nickname', 'email', 'username', 'password']

    def clean(self):
        password = self.cleaned_data.get('password')
        password_check = self.cleaned_data.get('password_check')
        if password != password_check:
            raise ValidationError({'password': 'Passwords do not match',
                                   'password_check': 'Passwords do not match'
                                   })

        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username).exists():
            raise ValidationError({'username': 'Username is already taken'})

        valid = re.compile(r"^[a-zA-Z0-9_]+$")
        if not valid.match(self.cleaned_data.get('username')):
            raise ValidationError({'username': 'Username may consists of characters a-z, A-Z, 0-9, _'})

        if not valid.match(self.cleaned_data.get('nickname')):
            raise ValidationError({'nickname': 'Nickname may consists of characters a-z, A-Z, 0-9, _'})

    def save(self, **kwargs):
        self.cleaned_data.pop('password_check')
        nickname = self.cleaned_data.pop('nickname')
        user = User.objects.create_user(**self.cleaned_data)
        user.save()

        profile = Profile(user=user, nickname=nickname)
        profile.save()
        return user


class EditUserForm(forms.ModelForm):
    username = forms.CharField(min_length=5,
                               max_length=50,
                               widget=forms.TextInput(attrs={"class": "input-control"}),
                               required=True
                               )
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "input-control"}),
                            required=True
                            )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username).exists():
            raise ValidationError({'username': 'Username is already taken'})

        valid = re.compile(r"^[a-zA-Z0-9_]+$")
        if not valid.match(self.cleaned_data.get('username')):
            raise ValidationError({'username': 'Username may consists of characters a-z, A-Z, 0-9, _'})


class EditProfileForm(forms.ModelForm):
    nickname = forms.CharField(min_length=3,
                               max_length=50,
                               widget=forms.TextInput(attrs={"class": "input-control"}),
                               required=True
                               )

    class Meta:
        model = Profile
        fields = ['nickname']

    def clean(self):
        valid = re.compile(r"^[a-zA-Z0-9_]+$")
        if not valid.match(self.cleaned_data.get('nickname')):
            raise ValidationError('Nickname may consists of characters a-z, A-Z, 0-9, _')


class QuestionForm(forms.ModelForm):
    title = forms.CharField(max_length=255,
                            min_length=3,
                            widget=forms.TextInput(attrs={"class": "input-control"}),
                            required=True
                            )
    content = forms.CharField(min_length=20,
                              widget=forms.Textarea(attrs={"class": "input-control-big-field"}),
                              required=True
                              )
    tags = forms.CharField(max_length=255,
                           widget=forms.TextInput(attrs={"class": "input-control"}),
                           required=True
                           )

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']

    def clean(self):
        valid = re.compile(r"^(?:[a-zA-Z_]+, ){0,2}[a-zA-Z_]+$")
        if not valid.match(self.cleaned_data.get('tags')):
            raise ValidationError('Valid tags should be like: cat, dog, elf\n Max: 3 tags')

    def save(self, **kwargs):
        user = Profile.objects.get(user=self.instance.profile)
        question = Question(user=user,
                            title=self.cleaned_data.get('title'),
                            content=self.cleaned_data.get('content'),
                            date_add=datetime.now()
                            )
        question.save()

        tags = self.cleaned_data.pop('tags').split(', ')
        for tag in tags:
            try:
                Tag.objects.get(tag_name=tag)
            except:
                new_tag = Tag(tag_name=tag)
                new_tag.save()
        tags_id = Tag.objects.filter(tag_name__in=tags).values('pk')
        for tag_id in tags_id:
            question_tag = QuestionTag(question=question,
                                       tag=Tag.objects.get(pk=tag_id['pk'])
                                       )
            question_tag.save()
        return question.pk


class AnswerForm(forms.ModelForm):
    content = forms.CharField(min_length=10,
                              widget=forms.Textarea(attrs={"class": "input-control-big-field"}),
                              required=True
                              )

    class Meta:
        model = Answer
        fields = ['content']

    def save(self, **kwargs):
        user = Profile.objects.get(user=self.instance.profile)
        question = Question.objects.get(pk=self.instance.question.pk)
        answer = Answer(user=user,
                        question=question,
                        content=self.cleaned_data.get('content'),
                        status=False
                        )
        answer.save()
        return answer.pk

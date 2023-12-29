import time

from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
from django.conf import settings as conf_settings

import itertools
import jwt
import time

from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from .forms import LoginForm, RegisterForm, EditUserForm, EditProfileForm, QuestionForm, AnswerForm
from . models import Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile


QTY_ON_PAGE = 20


def get_centrifugo_data(user_id: str) -> dict:
    return {
        'centrifugo': {
            'token': jwt.encode({"sub": str(user_id),
                                 "exp": int(time.time()) + 5 * 60},
                                conf_settings.CENTRIFUGO_TOKEN_HMAC_SECRET_KEY,
                                algorithm="HS256"),
            'ws_url': conf_settings.CENTRIFUGO_WS_URL
        }
    }


def error(request):
    return render(request, 'base/error.html')


def paginate(request, objects: list, per_page=QTY_ON_PAGE):
    page = request.GET.get('page', '1')
    paginator = Paginator(objects, per_page)
    try:
        page_obj = paginator.get_page(page)
    except EmptyPage:
        return error(request)
    except PageNotAnInteger:
        return error(request)
    return page_obj, page


def index(request):
    items = Question.manager.sort_by_latest(100)
    page_obj, page = paginate(request, items)
    return render(request, 'base/index.html',
                  {'questions': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
                   })


@csrf_protect
def question(request, question_id: int):
    item = Question.manager.question_by_id(question_id)
    answers = Answer.manager.answers_on_question(question_id)
    page_obj, page = paginate(request, answers)

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer_form.instance.profile = request.user
            answer_form.instance.question = Question.objects.get(pk=question_id)
            answer = answer_form.save()
            if answer:
                return redirect('/question/' + str(question_id) + '/#' + str(answer))
            else:
                answer_form.add_error(None, 'Answer posting error')
    else:
        answer_form = AnswerForm()

    return render(request, 'base/question.html',
                  {'question': item,
                   'answers': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members(),
                   'form': answer_form,
                   **get_centrifugo_data(request.user.id)
                   })


def tag(request, tag_name: str):
    items = Question.manager.filter_by_tag(tag_name)
    page_obj, page = paginate(request, items)
    return render(request, 'base/tag.html',
                  {'questions': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'tag': tag_name,
                   'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
                   })


def hot(request):
    items = Question.manager.sort_by_hot()
    page_obj, page = paginate(request, items)
    return render(request, 'base/index.html',
                  {'questions': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
                   })


@csrf_protect
def log_in(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user:
                login(request, user)
                # print('Successfully logged in')
                return redirect(request.GET.get('continue', '/'))
            else:
                login_form.add_error(None, 'Wrong password')
    else:
        login_form = LoginForm()
    return render(request,
                  'base/login.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members(),
                   'form': login_form
                   })


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_protect
def signup(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            if user:
                return redirect(reverse('index'))
            else:
                user_form.add_error(None, 'User saving error')
    else:
        user_form = RegisterForm()
    return render(request, 'base/signup.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members(),
                   'form': user_form
                   })


@login_required(login_url='login', redirect_field_name='continue')
@csrf_protect
def ask(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question_form.instance.profile = request.user
            question = question_form.save()
            if question:
                return redirect('/question/' + str(question))
            else:
                question_form.add_error(None, 'Question posting error')
    else:
        question_form = QuestionForm()
    return render(request, 'base/ask.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members(),
                   'form': question_form
                   })


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def edit(request):
    user_form = EditUserForm()
    profile_form = EditProfileForm()

    if request.method == 'GET':
        user_form = EditUserForm(instance=request.user)
        profile_form = EditProfileForm(instance=request.user.profile)

    elif request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save()
            if user and profile:
                return redirect(reverse('edit'))
            else:
                user_form.add_error(None, 'User saving error')

    return render(request, 'base/edit.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members(),
                   'user_form': user_form,
                   'profile_form': profile_form
                   })


@csrf_protect
@login_required
def like(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(Question, pk=question_id)
    LikeQuestion.manager.toggle_like(user=request.user.profile, question=question, like_value=1)
    try:
         count = Question.manager.likes_count(question_id)[0]['sum_likes']
    except:
         count = 0
    return JsonResponse({
        'count': count
    })


@csrf_protect
@login_required
def dislike(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(Question, pk=question_id)
    LikeQuestion.manager.toggle_like(user=request.user.profile, question=question, like_value=-1)
    try:
         count = Question.manager.likes_count(question_id)[0]['sum_likes']
    except:
         count = 0
    return JsonResponse({
        'count': count
    })


@csrf_protect
@login_required
def like_answer(request):
    answer_id = request.POST.get('answer_id')
    answer = get_object_or_404(Answer, pk=answer_id)
    LikeAnswer.manager.toggle_like(user=request.user.profile, answer=answer, like_value=1)
    try:
         count = Answer.manager.likes_count(answer_id)[0]['sum_likes']
    except:
         count = 0
    return JsonResponse({
        'count': count
    })


@csrf_protect
@login_required
def dislike_answer(request):
    answer_id = request.POST.get('answer_id')
    answer = get_object_or_404(Answer, pk=answer_id)
    LikeAnswer.manager.toggle_like(user=request.user.profile, answer=answer, like_value=-1)
    try:
         count = Answer.manager.likes_count(answer_id)[0]['sum_likes']
    except:
         count = 0
    return JsonResponse({
        'count': count
    })


@csrf_protect
@login_required
def correct(request):
    answer_id = request.POST.get('answer_id')
    question_id = request.POST.get('question_id')
    answer = get_object_or_404(Answer, pk=answer_id)
    question = get_object_or_404(Question, pk=question_id)
    Answer.manager.toggle_correct(user=request.user.profile, question=question, answer=answer)
    return JsonResponse({})

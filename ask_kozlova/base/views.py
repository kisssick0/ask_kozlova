import time
import itertools
import jwt
import time
from cent import Client
from faker import Faker

from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
from django.conf import settings as conf_settings
from django.template.loader import render_to_string
from django.core.cache import cache

from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm, EditUserForm, EditProfileForm, QuestionForm, AnswerForm
from . models import Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile


fake = Faker()

QTY_ON_PAGE = 20

client = Client(conf_settings.CENTRIFUGO_API_URL, api_key=conf_settings.CENTRIFUGO_API_KEY, timeout=1)


def cache_popular_tags():
    tags = Tag.manager.popular_tags()
    cache_key = 'popular_tags'
    # tags = [{"tag_name": fake.unique.user_name()} for i in range(10)]
    cache.set(cache_key, tags, 10)


def get_popular_tags():
    cache_key = 'popular_tags'
    tags = cache.get(cache_key)

    # if not tags:
    #     cache_popular_tags()
    return tags


def cache_best_members():
    best_members = Profile.manager.best_members()
    cache_key = 'best_members'
    # best_members = [fake.unique.user_name() for i in range(10)]
    cache.set(cache_key, best_members, 10)


def get_best_members():
    cache_key = 'best_members'
    best_members = cache.get(cache_key)

    # if not best_members:
    #     cache_best_members()
    return best_members


def get_centrifugo_data(user_id: str, channel: str) -> dict:
    return {
        'centrifugo': {
            'token': jwt.encode({"sub": str(user_id),
                                 "exp": int(time.time()) + 5 * 60},
                                conf_settings.CENTRIFUGO_TOKEN_HMAC_SECRET_KEY,
                                algorithm="HS256"),
            'ws_url': conf_settings.CENTRIFUGO_WS_URL,
            'channel': channel
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
                   'popular_tags': get_popular_tags(),
                   'best_members': get_best_members()
                   })


@csrf_protect
def question(request, question_id: int):
    item = Question.manager.question_by_id(question_id)
    answers = Answer.manager.answers_on_question(question_id)
    page_obj, page = paginate(request, answers)

    answer_form = AnswerForm()

    try:
        answer_form.instance.user = request.user.profile
        answer_form.instance.question = Question.objects.get(pk=question_id)
    except:
        pass

    return render(request, 'base/question.html',
                  {'question': item,
                   'answers': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'popular_tags': get_popular_tags(),
                   'best_members': get_best_members(),
                   'form': answer_form,
                   **get_centrifugo_data(request.user.id, f'question.{question_id}')
                   })


@csrf_protect
@login_required
def comment(request):
    answer = Answer()
    answer.user = get_object_or_404(Profile, pk=request.POST.get('user'))
    answer.question = get_object_or_404(Question, pk=request.POST.get('question'))
    answer.content = request.POST.get("content")

    answer.save()

    client.publish(f'question.{request.POST.get("question")}', model_to_dict(answer))

    return JsonResponse({
        'avatar_url': answer.user.avatar.url,
        'likes_count': 0,
        'content': answer.content
        })


def tag(request, tag_name: str):
    items = Question.manager.filter_by_tag(tag_name)
    page_obj, page = paginate(request, items)
    return render(request, 'base/tag.html',
                  {'questions': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'tag': tag_name,
                   'popular_tags': get_popular_tags(),
                   'best_members': get_best_members()
                   })


def hot(request):
    items = Question.manager.sort_by_hot()
    page_obj, page = paginate(request, items)
    return render(request, 'base/index.html',
                  {'questions': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'popular_tags': get_popular_tags(),
                   'best_members': get_best_members()
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
                  {'popular_tags': get_popular_tags(),
                   'best_members': get_best_members(),
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
                  {'popular_tags': get_popular_tags(),
                   'best_members': get_best_members(),
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
                  {'popular_tags': get_popular_tags(),
                   'best_members': get_best_members(),
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
                  {'popular_tags': get_popular_tags(),
                   'best_members': get_best_members(),
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

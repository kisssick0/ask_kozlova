from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import itertools
from . models import Question, Answer, Tag, LikeQuestion, LikeAnswer, Profile


QTY_ON_PAGE = 20


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


def question(request, question_id: int):
    item = Question.manager.question_by_id(question_id)
    answers = Answer.manager.answers_on_question(question_id)
    page_obj, page = paginate(request, answers)
    return render(request, 'base/question.html',
                  {'question': item,
                   'answers': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
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


def login(request):
    return render(request, 'base/login.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
                   })


def signup(request):
    return render(request, 'base/signup.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
                   })


def ask(request):
    return render(request, 'base/ask.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
                   })


def settings(request):
    return render(request, 'base/settings.html',
                  {'popular_tags': Tag.manager.popular_tags(),
                   'best_members': Profile.manager.best_members()
                   })

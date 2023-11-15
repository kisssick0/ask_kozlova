from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
import itertools
# Create your views here.


def gen_number(start: int, end: int):
    while start != end:
        yield start
        start += 1


QTY = 120
QTY_ON_PAGE = 20
PAGE_QTY = QTY // QTY_ON_PAGE


ANSWERS = [
    {
        'id': i,
        'title': f'Title {i}',
        'content': f'{i} Everything is going great! The sun is shining, the birds are singing, and I feel fantastic. '
                   f'I have a wonderful job, amazing friends, and a loving family. Im in good health and have '
                   f'everything I need. I feel grateful for all the blessings in my life and Im excited for the '
                   f'future. Im surrounded by positivity and love, and Im filled with joy and happiness. '
                   f'I have so much to look forward to and I cant wait to see what the future holds. Life is good and '
                   f'I am truly blessed.'
    } for i in range(QTY)
]


TAGS = [
    {
        'index': itertools.cycle([]),
        'tag_names': ['Python', 'Ruby', 'Cpp', 'HTML', 'WASM']
    } for i in range(QTY)
]
c = itertools.cycle(gen_number(0, len(TAGS[0]['tag_names'])))
TAGS[0]['index'] = c


QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'content': f'I have problem {i}',
        'tag': TAGS[0]['tag_names'][next(TAGS[0]['index'])],
    } for i in range(QTY)
]


# def paginate(objects: any, page: int, per_page=QTY_ON_PAGE):
    # paginator = Paginator(objects, per_page)
    # page_items = paginator.page(page).object_list
    # return page_items


def index(request):
    page = request.GET.get('page', 1)
    paginator = Paginator(QUESTIONS, QTY_ON_PAGE)
    page_obj = paginator.get_page(page)
    return render(request, 'base/index.html',
                  # {'questions': paginate(QUESTIONS, page=page),
                  {'questions': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'pages': [i + 1 for i in range(PAGE_QTY)],
                   'answer_qty': len(ANSWERS)
                   })


def question(request, question_id):
    item = QUESTIONS[question_id]

    page = request.GET.get('page', 1)
    paginator = Paginator(ANSWERS, QTY_ON_PAGE)
    page_obj = paginator.get_page(page)
    return render(request, 'base/question.html',
                  {'question': item,
                   'answers': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'pages': [i + 1 for i in range(PAGE_QTY)],
                   'answer_qty': len(ANSWERS)
                   })


def tag(request, tag_name):
    page = request.GET.get('page', 1)
    questions_with_tag = [QUESTIONS[i] for i in range(QTY) if QUESTIONS[i]['tag'].lower() == tag_name.lower()]
    paginator = Paginator(questions_with_tag, QTY_ON_PAGE)
    page_obj = paginator.get_page(page)
    return render(request, 'base/tag.html',
                  # {'questions': paginate(questions_with_tag, page=page),
                  {'questions': page_obj,
                   'page_obj': page_obj,
                   'page': page,
                   'tag': tag_name,
                   'pages': [i + 1 for i in range(PAGE_QTY)],
                   'answer_qty': len(ANSWERS)
                   })


def hot(request):
    return render(request, 'base/index.html')


def login(request):
    return render(request, 'base/login.html')


def signup(request):
    return render(request, 'base/signup.html')


def ask(request):
    return render(request, 'base/ask.html')


def settings(request):
    return render(request, 'base/settings.html')

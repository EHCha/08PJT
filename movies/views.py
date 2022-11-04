from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .models import Genre, Movie
from .forms import GenreForm, MovieForm
from random import *

# Create your views here.
@require_safe
def index(request):
    movies = Movie.objects.all()
    context = {
        'movies': movies,
    }
    return render(request, 'movies/index.html', context)

@require_safe
def detail(request, movie_pk):
    movie = Movie.objects.get(pk=movie_pk)
    context = {
        'movie': movie,
    }
    return render(request, 'movies/detail.html', context)

@require_safe
def recommended(request):
    movies2 = Movie.objects.filter(vote_count__gte=6000, vote_average__gte=8)
    many = movies2.count()
    num = randrange(0, many-1)
    goodmovie = movies2[num]

    context = {
        'movies2': movies2[:40],
        'goodmovie':goodmovie,
    }
    return render(request, 'movies/recommended.html', context)
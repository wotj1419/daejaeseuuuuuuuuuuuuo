from django.contrib import admin
from .models import Movie, Genre

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'vote_average', 'release_date')
    list_filter = ('genres',)
    search_fields = ('title',)

admin.site.register(Genre)

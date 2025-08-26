from django.contrib import admin
from .models import Poll, Option, Vote

class OptionInline(admin.TabularInline):
    model = Option
    extra = 3

class PollAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ['question', 'created_by', 'created_at', 'is_active', 'total_votes']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question']

class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'option', 'voted_at']
    list_filter = ['voted_at', 'option__poll']

admin.site.register(Poll, PollAdmin)
admin.site.register(Option)
admin.site.register(Vote, VoteAdmin)
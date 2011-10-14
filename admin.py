import datetime

from django.contrib import admin

from models import Entry, Category, Link
from forms import EntryAdminModelForm, LinkAdminModelForm, CategoryAdminModelForm


class Media:
    js = ('/media_root/wymeditor/plugins/jquery.wymeditor.filebrowser.js',)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    form = CategoryAdminModelForm

class LinkAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    form = LinkAdminModelForm

class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['headline']}
    form = EntryAdminModelForm



admin.site.register(Category, CategoryAdmin),
admin.site.register(Link, LinkAdmin),
admin.site.register(Entry, EntryAdmin),


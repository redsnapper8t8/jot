import datetime
from django import template
from blog.models import Entry
#from zeus.apps.blog.models import Category

register = template.Library()

@register.inclusion_tag('blog/entry_snippet.html')
def render_latest_blog_entries(num):
    entries = Entry.live.filter(pub_date__lte=datetime.datetime.now())[:num]
    return {
        'entries': entries,
    }

@register.inclusion_tag('blog/month_links_snippet.html')
def render_month_links():
    return {
        'dates': Entry.live.dates('pub_date', 'month'),
    }


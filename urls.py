from django.conf.urls.defaults import *
#import django.views.generic.list_detail
from django.contrib.sites.models import Site
from django.views.generic.list_detail import object_list
from django.contrib.comments.feeds import LatestCommentFeed
from jot.feeds import WeblogEntryFeed
from tagging.views import tagged_object_list
from tagging.models import Tag 


from models import Entry
#, Category 
#from views import category_detail

site = Site.objects.get_current()

info_dict = {
    'queryset': Entry.live.all(),
    'date_field': 'pub_date',
    }

feeds = {
    'entries': WeblogEntryFeed,
    'comments': LatestCommentFeed,
}


urlpatterns = patterns('django.views.generic.date_based',
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\w-]+)/$', 
	'object_detail', 
	dict(info_dict, slug_field='slug')),

   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', 'archive_day',
	info_dict),

   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'archive_month', info_dict),

   (r'^(?P<year>\d{4})/$', 'archive_year', info_dict, 
	'blog_entry_archive_year'),

   (r'^/?$', 'archive_index', info_dict, 'blog_entry_index'),
)

urlpatterns += patterns('',
   #(r'^category/', include('category.urls')),
   (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', 
	{'feed_dict': feeds}),

   (r'^tag/(?P<tag>[^/]+(?u))/$','tagging.views.tagged_object_list', 
	dict(queryset_or_model=Entry.live.all(), 
	template_name='blog/entry_tag_list.html')),
)



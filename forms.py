from django import forms
from django.db.models import get_model
from blog.widgets import WYMEditor, BasicWYMEditor

class EntryAdminModelForm(forms.ModelForm):
    body = forms.CharField(widget=WYMEditor())
    summary = forms.CharField(widget=BasicWYMEditor())

    class Meta:
        model = get_model('blog', 'entry')

class LinkAdminModelForm(forms.ModelForm):
    description = forms.CharField(widget=WYMEditor())

    class Meta:
        model = get_model('blog', 'link')

class CategoryAdminModelForm(forms.ModelForm):
    description = forms.CharField(widget=WYMEditor())

    class Meta:
        model = get_model('blog', 'category')


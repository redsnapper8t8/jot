from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class WYMEditor(forms.Textarea):
    class Media:
        js = (
            '/media_root/jquery/jquery.js',
            '/media_root/wymeditor/jquery.wymeditor.js',
            '/media_root/wymeditor/plugins/jquery.wymeditor.filebrowser.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.attrs = {'class': 'wymeditor'}
        if attrs:
            self.attrs.update(attrs)
        super(WYMEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(WYMEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            jQuery('#id_%s').wymeditor({
                updateSelector: '.submit-row input[type=submit]',
                updateEvent: 'click',
                lang: '%s',
                logoHtml: '',
                postInitDialog: wymeditor_filebrowser, 
            });
            </script>''' % (name, self.language))

class BasicWYMEditor(WYMEditor):
    def render(self, name, value, attrs=None):
        rendered = super(WYMEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            jQuery('#id_%s').wymeditor({
                updateSelector: '.submit-row input[type=submit]',
                updateEvent: 'click',
                lang: '%s',
                dialogFeatures: 'menubar=no,titlebar=no,toolbar=no',
                logoHtml: '',
                toolsItems: [
                    {'name': 'Bold', 'title': 'Strong', 'css': 'wym_tools_strong'}, 
                    {'name': 'Italic', 'title': 'Emphasis', 'css': 'wym_tools_emphasis'},
                    {'name': 'ToggleHtml', 'title': 'HTML', 'css': 'wym_tools_html'}
                ]

            });
            </script>''' % (name, self.language))
    

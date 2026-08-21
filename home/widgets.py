from django import forms
from django.utils.html import format_html

class TinyMCERichTextArea(forms.Widget):
    template_name = 'home/widgets/tinymce.html'

    def __init__(self, attrs=None, options=None):
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['name'] = name
        attrs['class'] = attrs.get('class', '') + ' tinymce-editor'
        value_str = value or ''
        if 'id' not in attrs:
            attrs['id'] = f"id_{name}"
        return format_html('<textarea id="{}" name="{}" class="{}">{}</textarea>', attrs['id'], name, attrs['class'], value_str)

    @property
    def media(self):
        return forms.Media(
            js=[
                'https://cdn.jsdelivr.net/npm/tinymce@6/tinymce.min.js',
                'home/js/tinymce_init.js',
            ]
        )

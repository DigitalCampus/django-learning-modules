# learning_modules/templatetags/display_functions.py
import json
from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter(name='get_title')
@stringfilter
def get_title(title,lang):
    try:
        titles = json.loads(title)
        if lang in titles:
            return titles[lang]
        else:
            for l in titles:
                return titles[l]
    except:
        pass
    return title
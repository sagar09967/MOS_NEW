from django import template

register = template.Library()

@register.filter
def get_by_index(indexable, i):
    return indexable[i]

@register.filter
def get_by_key(dict_like, key):
    return dict_like[key]
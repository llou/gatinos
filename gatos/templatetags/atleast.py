from django import template
from django.utils.safestring import mark_safe

register = template.Library()


class DumbObject:
    def __getattr__(self, name):
        return mark_safe("")

    def __getitem__(self, name):
        return mark_safe("")

    def __bool__(self):
        return False


@register.filter
def atleast(iterable, upto):
    data = list(iterable)
    if len(data) >= upto:
        return data[:upto]
    return data + [DumbObject()] * (upto - len(data))

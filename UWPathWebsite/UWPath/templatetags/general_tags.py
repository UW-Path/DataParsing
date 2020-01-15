from django import template

register = template.Library()

@register.simple_tag()
def get_degree_major(major):
    return str(major)

@register.filter(name='strip_spaces')
def strip_spaces(s):
    return s.replace(" ", "")

@register.filter(name='times')
def times(number):
    return range(number)

# @register.simple_tag
# def get_major(major):
#     return rates.get(crit=crit).rate

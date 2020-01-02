from django import template

register = template.Library()

@register.simple_tag()
def get_degree_major(major):
    return str(major)

# @register.simple_tag
# def get_major(major):
#     return rates.get(crit=crit).rate

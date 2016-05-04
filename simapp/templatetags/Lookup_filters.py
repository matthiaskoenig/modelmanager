"""
Created on Jun 24, 2014

@author: Matthias Koenig
@date: 2014-06-24
"""

from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

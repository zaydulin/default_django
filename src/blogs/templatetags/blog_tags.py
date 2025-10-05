from django import template

register = template.Library()

@register.simple_tag
def get_first_blog_slug(blogs):
    if blogs.exists():
        return blogs.first().slug
    return None
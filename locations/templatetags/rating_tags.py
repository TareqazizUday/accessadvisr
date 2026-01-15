from django import template

register = template.Library()

@register.inclusion_tag('components/star_rating.html')
def star_rating(rating):
    """Display star rating based on a numeric rating (0-5)"""
    full_stars = int(rating)
    has_half_star = (rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if has_half_star else 0)
    
    return {
        'full_stars': range(full_stars),
        'has_half_star': has_half_star,
        'empty_stars': range(empty_stars),
        'rating': rating
    }

from django import template

register = template.Library()


@register.filter
def get_place_photo_url(photo_obj, api_key):
    """
    Build a Google Place Photo URL from a photo reference dict.
    Usage in template: {{ photo|get_place_photo_url:GOOGLE_MAPS_API_KEY }}
    """
    if not photo_obj or not api_key:
        return ''

    ref = None
    if isinstance(photo_obj, dict):
        ref = photo_obj.get('photo_reference')
    else:
        ref = getattr(photo_obj, 'photo_reference', None)

    if not ref:
        return ''

    # Use mark_safe to prevent HTML entity encoding of & in URLs
    from django.utils.safestring import mark_safe
    url = (
        f'https://maps.googleapis.com/maps/api/place/photo'
        f'?maxwidth=800&photoreference={ref}&key={api_key}'
    )
    return mark_safe(url)




from django import template

register = template.Library()

# Map category types to YouTube video IDs from AccessAdvisr channel
# Channel: https://www.youtube.com/channel/UCpEpBkHu-4ls7hxcAboVOTQ
CATEGORY_VIDEO_MAP = {
    'education': 'c7Oy4ojSwyE',  # AccessAdvisr Channel Video 1
    'school': 'c7Oy4ojSwyE',
    'university': 'SZEflIVnhH8',  # AccessAdvisr Channel Video 2
    'library': 'SZEflIVnhH8',
    
    'food': 'a4k2wJcIAR4',  # Real Reviews. True Access
    'restaurant': 'a4k2wJcIAR4',
    'cafe': 'a4k2wJcIAR4',
    'bar': 'a4k2wJcIAR4',
    'food_and_restaurants': 'a4k2wJcIAR4',
    
    'entertainment': '5gGCfJh1Q3Q',  # Disabled Voices Are LEADING The Way
    'movie_theater': '5gGCfJh1Q3Q',
    'amusement_park': '5gGCfJh1Q3Q',
    'theater': '5gGCfJh1Q3Q',
    
    'shopping': 'c7Oy4ojSwyE',  # AccessAdvisr Channel Video 1
    'shopping_mall': 'c7Oy4ojSwyE',
    'store': 'c7Oy4ojSwyE',
    
    'sport': 'SZEflIVnhH8',  # AccessAdvisr Channel Video 2
    'gym': 'SZEflIVnhH8',
    'stadium': 'SZEflIVnhH8',
    
    'travel': 'a4k2wJcIAR4',  # Real Reviews. True Access
    'hotel': 'a4k2wJcIAR4',
    'travel_agency': 'a4k2wJcIAR4',
    'tourist_attraction': 'a4k2wJcIAR4',
    'travel_and_tour': 'a4k2wJcIAR4',
    
    'airport': '5gGCfJh1Q3Q',  # Disabled Voices Are LEADING The Way
    'transit_station': '5gGCfJh1Q3Q',
    'train_station': '5gGCfJh1Q3Q',
    'bus_station': '5gGCfJh1Q3Q',
    
    'museum': 'c7Oy4ojSwyE',  # AccessAdvisr Channel Video 1
    'art_gallery': 'c7Oy4ojSwyE',
    
    'park': 'SZEflIVnhH8',  # AccessAdvisr Channel Video 2
    'beach': 'SZEflIVnhH8',
    
    'community': 'a4k2wJcIAR4',  # Real Reviews. True Access
    'community_center': 'a4k2wJcIAR4',
    
    # Default videos
    'default': 'a4k2wJcIAR4',  # Real Reviews. True Access (Main video)
}

@register.simple_tag
def get_category_video(location=None, place_types=None):
    """
    Get the appropriate YouTube video ID based on location category or place types.
    
    Args:
        location: Location object from database
        place_types: List of place types from Google Places API
    
    Returns:
        YouTube video ID string
    """
    video_id = None
    
    # First check if location has a video_url
    if location and hasattr(location, 'video_url') and location.video_url:
        # Extract video ID from YouTube URL
        url = location.video_url
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('watch?v=')[-1].split('&')[0]
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        elif 'youtube.com/embed/' in url:
            video_id = url.split('embed/')[-1].split('?')[0]
        
        if video_id:
            return video_id
    
    # Check location category
    if location and hasattr(location, 'category') and location.category:
        category_name = location.category.name.lower().replace(' ', '_').replace('&', 'and')
        video_id = CATEGORY_VIDEO_MAP.get(category_name)
        if video_id:
            return video_id
    
    # Check Google Place types
    if place_types and isinstance(place_types, list):
        for place_type in place_types:
            place_type_clean = place_type.lower().replace(' ', '_')
            video_id = CATEGORY_VIDEO_MAP.get(place_type_clean)
            if video_id:
                return video_id
    
    # Return default video
    return CATEGORY_VIDEO_MAP['default']


@register.simple_tag
def get_video_embed_url(location=None, place_types=None, request=None):
    """
    Get the full YouTube embed URL with all required parameters.
    
    Args:
        location: Location object from database
        place_types: List of place types from Google Places API
        request: HTTP request object for origin
    
    Returns:
        Full YouTube embed URL string
    """
    video_id = get_category_video(location, place_types)
    
    # Build origin from request
    origin = ''
    if request:
        origin = f"{request.scheme}://{request.get_host()}"
    
    # Build full embed URL with parameters
    embed_url = f"https://www.youtube.com/embed/{video_id}?enablejsapi=1&rel=0"
    if origin:
        embed_url += f"&origin={origin}"
    
    return embed_url

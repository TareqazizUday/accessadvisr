from django import template
import re

register = template.Library()


@register.filter
def youtube_embed_id(url):
    """Extract YouTube video ID from various YouTube URL formats"""
    if not url:
        return ''
    
    # Pattern to match YouTube video IDs
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If it's already an embed URL, extract the ID
    if 'youtube.com/embed/' in url:
        video_id = url.split('youtube.com/embed/')[-1].split('?')[0]
        if len(video_id) == 11:  # Valid YouTube ID length
            return video_id
    
    return ''


@register.filter
def youtube_embed_url(url):
    """Convert YouTube URL to embed URL (without query parameters, they should be added in template)"""
    if not url:
        return ''
    
    video_id = youtube_embed_id(url)
    if video_id:
        # Return clean embed URL without query params
        # Query params like enablejsapi, origin, rel should be added in template
        return f'https://www.youtube.com/embed/{video_id}'
    
    # If it's already an embed URL, clean it up (remove query params)
    if 'youtube.com/embed/' in url:
        embed_url = url.split('youtube.com/embed/')[1]
        video_id = embed_url.split('?')[0].split('/')[0]
        if len(video_id) == 11:  # Valid YouTube ID length
            return f'https://www.youtube.com/embed/{video_id}'
    
    return url



from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
import os


class RobotsView(View):
    """Serve robots.txt file"""
    
    def get(self, request):
        robots_path = os.path.join(settings.STATIC_ROOT if not settings.DEBUG else os.path.join(settings.BASE_DIR, 'static'), 'robots.txt')
        
        try:
            with open(robots_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = """User-agent: *
Allow: /

Sitemap: {}/sitemap.xml

Disallow: /admin/
Disallow: /api/auth/
Disallow: /api/reviews/
Disallow: /api/profile/
Disallow: /api/partner-comments/
Disallow: /api/blog-comments/
Disallow: /api/about-comments/
Disallow: /api/donations/
""".format(request.build_absolute_uri('/'))
        
        # Replace placeholder with actual domain
        if 'yoursite.com' in content:
            domain = request.build_absolute_uri('/')
            content = content.replace('https://yoursite.com/', domain)
        
        return HttpResponse(content, content_type='text/plain')
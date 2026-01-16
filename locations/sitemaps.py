from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Blog, Partner, AboutPost, Location


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'about',
            'blogs',
            'partners',
            'contact',
            'donate',
            'packages',
            'browse',
            'listings',
            'accommodation',
            'entertainment',
            'food-drink',
            'shopping',
            'sports-recreational',
            'transport',
            'flight-travel',
            'education',
            'all-contributions',
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Blog.objects.filter(status='published').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class PartnerSitemap(Sitemap):
    """Sitemap for partner pages"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Partner.objects.filter(status='published').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class AboutPostSitemap(Sitemap):
    """Sitemap for about posts"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return AboutPost.objects.filter(status='published').order_by('order')

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class LocationSitemap(Sitemap):
    """Sitemap for location detail pages"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        # Get active locations from database
        locations = Location.objects.filter(status='active').order_by('-created_at')[:500]  # Limit to 500 for performance
        return locations

    def location(self, obj):
        # Use place_id if available, otherwise use primary key
        place_id = obj.place_id or str(obj.id)
        return reverse('place-detail', kwargs={'place_id': place_id})

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at

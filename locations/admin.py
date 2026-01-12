from django.contrib import admin
from .models import Location, Category, Amenity, Review, ReviewReply


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'latitude', 'longitude', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['name', 'keywords']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['amenities']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'status')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Content', {
            'fields': ('description', 'what_we_looking_for', 'why_this_matters', 'how_to_apply')
        }),
        ('Contact & Links', {
            'fields': ('email', 'website', 'video_url')
        }),
        ('Social Media', {
            'fields': ('social_facebook', 'social_twitter', 'social_google_plus', 'social_pinterest'),
            'classes': ('collapse',)
        }),
        ('Features', {
            'fields': ('amenities', 'keywords')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'place_name', 'get_average_rating', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'place_id']
    search_fields = ['author_name', 'author_email', 'place_name', 'review_text']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Place Information', {
            'fields': ('place_id', 'place_name')
        }),
        ('Reviewer Information', {
            'fields': ('author_name', 'author_email', 'save_info')
        }),
        ('Ratings', {
            'fields': ('quality_rating', 'location_rating', 'service_rating', 'price_rating')
        }),
        ('Review Content', {
            'fields': ('review_text',)
        }),
        ('Engagement', {
            'fields': ('likes', 'dislikes', 'hearts')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    get_average_rating.short_description = 'Avg Rating'


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'review', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['author_name', 'author_email', 'reply_text']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Reply Information', {
            'fields': ('review', 'author_name', 'author_email', 'reply_text', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

from django.contrib import admin
from .models import Location, Category, Amenity, Review, ReviewReply, Blog, BlogComment, BlogCommentReply, Partner, PartnerComment, PartnerCommentReply, AboutPost, AboutComment, AboutCommentReply, DonationCampaign, Donation, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'created_at']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('profile_picture', 'bio', 'location', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'content', 'author']
    list_editable = ['status']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status'),
            'description': 'Enter the blog title, author, and status. Slug will be auto-generated from the title if left blank.'
        }),
        ('Content', {
            'fields': ('image', 'video_url', 'content'),
            'description': 'Upload blog image (optional), enter YouTube video URL (optional), and full blog post content. HTML is supported.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        """Only prepopulate slug when adding a new blog, not when editing"""
        if obj is None:  # Adding a new object
            return {'slug': ('title',)}
        return {}
    
    def get_readonly_fields(self, request, obj=None):
        """Make slug and timestamps readonly when editing, but allow slug to be auto-generated when adding"""
        readonly = ['created_at', 'updated_at']
        if obj:  # Editing an existing object
            readonly.append('slug')
        return readonly


@admin.register(PartnerComment)
class PartnerCommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'partner', 'created_at', 'is_active', 'is_approved']
    list_filter = ['is_active', 'is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'comment_text', 'partner__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'is_approved']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('partner', 'author_name', 'author_email', 'comment_text', 'save_info', 'is_active', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PartnerCommentReply)
class PartnerCommentReplyAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'comment', 'created_at', 'is_active', 'is_approved']
    list_filter = ['is_active', 'is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'reply_text', 'comment__partner__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'is_approved']
    
    fieldsets = (
        ('Reply Information', {
            'fields': ('comment', 'parent_reply', 'author_name', 'author_email', 'reply_text', 'is_active', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'blog', 'created_at', 'is_active', 'is_approved']
    list_filter = ['is_active', 'is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'comment_text', 'blog__title']
    readonly_fields = ['created_at', 'updated_at', 'is_approved']
    list_editable = ['is_active', 'is_approved']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('blog', 'author_name', 'author_email', 'comment_text', 'save_info', 'is_active', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlogCommentReply)
class BlogCommentReplyAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'comment', 'created_at', 'is_active', 'is_approved']
    list_filter = ['is_active', 'is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'reply_text', 'comment__blog__title']
    readonly_fields = ['created_at', 'updated_at', 'is_approved']
    list_editable = ['is_active', 'is_approved']
    
    fieldsets = (
        ('Reply Information', {
            'fields': ('comment', 'parent_reply', 'author_name', 'author_email', 'reply_text', 'is_active', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'content', 'author']
    list_editable = ['status']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status'),
            'description': 'Enter the partner title, author, and status. Slug will be auto-generated from the title if left blank.'
        }),
        ('Content', {
            'fields': ('image', 'video_url', 'website_url', 'content'),
            'description': 'Upload partner image (optional), enter video URL (optional), website URL (optional), and full partner post content. HTML is supported.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        """Only prepopulate slug when adding a new partner, not when editing"""
        if obj is None:  # Adding a new object
            return {'slug': ('title',)}
        return {}
    
    def get_readonly_fields(self, request, obj=None):
        """Make slug and timestamps readonly when editing, but allow slug to be auto-generated when adding"""
        readonly = ['created_at', 'updated_at']
        if obj:  # Editing an existing object
            readonly.append('slug')
        return readonly


@admin.register(AboutPost)
class AboutPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'status', 'share_this_post', 'created_at', 'updated_at']
    list_filter = ['status', 'share_this_post', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['order', 'status', 'share_this_post']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'order', 'status'),
            'description': 'Enter the about post title, display order, and status. Slug will be auto-generated from the title if left blank. Lower order numbers appear first.'
        }),
        ('Content', {
            'fields': ('image', 'content'),
            'description': 'Upload featured image (optional) and full post content. HTML is supported.'
        }),
        ('Sharing', {
            'fields': ('share_this_post', 'share_facebook_url', 'share_twitter_url', 'share_linkedin_url', 'share_email_url'),
            'description': 'Enable or disable social sharing buttons. You can provide custom share URLs for each platform. If left blank, default share URLs will be used.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        """Only prepopulate slug when adding a new post, not when editing"""
        if obj is None:  # Adding a new object
            return {'slug': ('title',)}
        return {}
    
    def get_readonly_fields(self, request, obj=None):
        """Make slug and timestamps readonly when editing"""
        readonly = ['created_at', 'updated_at']
        if obj:  # Editing an existing object
            readonly.append('slug')
        return readonly


@admin.register(AboutComment)
class AboutCommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'about_post', 'created_at', 'is_active', 'is_approved']
    list_filter = ['is_active', 'is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'comment_text', 'about_post__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'is_approved']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('about_post', 'author_name', 'author_email', 'comment_text', 'save_info', 'is_active', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AboutCommentReply)
class AboutCommentReplyAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'comment', 'created_at', 'is_active', 'is_approved']
    list_filter = ['is_active', 'is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'reply_text', 'comment__about_post__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'is_approved']
    
    fieldsets = (
        ('Reply Information', {
            'fields': ('comment', 'parent_reply', 'author_name', 'author_email', 'reply_text', 'is_active', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DonationCampaign)
class DonationCampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_amount', 'raised_amount', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at', 'slug']
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('title', 'slug', 'image', 'description', 'is_active', 'order')
        }),
        ('Amounts', {
            'fields': ('target_amount', 'raised_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_prepopulated_fields(self, request, obj=None):
        """Only prepopulate slug when adding a new campaign"""
        if obj is None:
            return {'slug': ('title',)}
        return {}


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'get_final_amount', 'payment_method', 'status', 'campaign', 'created_at']
    list_filter = ['status', 'payment_method', 'donation_amount', 'created_at', 'campaign']
    search_fields = ['name', 'email', 'phone', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Campaign', {
            'fields': ('campaign',)
        }),
        ('Personal Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Address Information', {
            'fields': ('street_address', 'apartment_suite', 'city', 'state_province', 'zip_postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Donation Details', {
            'fields': ('donation_amount', 'custom_amount', 'payment_method', 'consent_given')
        }),
        ('Payment Status', {
            'fields': ('status', 'transaction_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_final_amount(self, obj):
        return f"£{obj.get_final_amount()}"
    get_final_amount.short_description = 'Amount'



from django.db import models


class Category(models.Model):
    """Category model for organizing locations"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji for the category")
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Amenity(models.Model):
    """Amenity model for location features"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji for the amenity")
    
    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Location(models.Model):
    """Location model for storing places with coordinates"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords for search")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    # New fields for detailed page
    description = models.TextField(blank=True, help_text="Main description of the location")
    what_we_looking_for = models.TextField(blank=True, help_text="What we're looking for section")
    why_this_matters = models.TextField(blank=True, help_text="Why this matters section")
    how_to_apply = models.TextField(blank=True, help_text="How to apply section")
    email = models.EmailField(blank=True, help_text="Contact email")
    website = models.URLField(blank=True, help_text="Website URL")
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    
    # Social media links
    social_facebook = models.URLField(blank=True, help_text="Facebook page URL")
    social_twitter = models.URLField(blank=True, help_text="Twitter/X profile URL")
    social_google_plus = models.URLField(blank=True, help_text="Google+ profile URL")
    social_pinterest = models.URLField(blank=True, help_text="Pinterest profile URL")
    
    # Many-to-many relationship with amenities
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='locations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def get_keywords_list(self):
        """Return keywords as a list"""
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',') if k.strip()]
        return []


class Review(models.Model):
    """Review model for storing user reviews of places"""
    place_id = models.CharField(max_length=255, help_text="Google Place ID")
    place_name = models.CharField(max_length=200, blank=True, help_text="Place name for reference")
    
    # User information
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField(blank=True)
    
    # Ratings (1-5 scale)
    quality_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    location_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    service_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    price_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    
    # Review content
    review_text = models.TextField()
    
    # Engagement counts
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    hearts = models.IntegerField(default=0)
    
    # Metadata
    save_info = models.BooleanField(default=False, help_text="User wants to save info for next time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['place_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Review by {self.author_name} for {self.place_name}"
    
    def get_average_rating(self):
        """Calculate average of all ratings"""
        return round((self.quality_rating + self.location_rating + self.service_rating + self.price_rating) / 4, 1)


class ReviewReply(models.Model):
    """Model for storing replies to reviews and nested replies"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', help_text="Parent reply if this is a nested reply")
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField(blank=True)
    reply_text = models.TextField()
    
    # Engagement counts
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    hearts = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Review Replies'
        indexes = [
            models.Index(fields=['review']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author_name} to review {self.review.id}"

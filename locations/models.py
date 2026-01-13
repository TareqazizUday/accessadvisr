from django.db import models
from django.utils.text import slugify
from django.conf import settings
import os

def partner_image_upload_path(instance, filename):
    """Generate upload path for partner images - uses slug to prevent duplicates"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Use partner slug as filename to prevent duplicates
    # If slug exists, use it; otherwise Django will handle it after save
    if instance.slug:
        filename = f"{instance.slug}.{ext}"
    elif instance.pk:
        # If we have a pk but no slug, use pk temporarily
        filename = f"partner_{instance.pk}.{ext}"
    else:
        # For new instances, use original filename (will be renamed on save)
        base_name = os.path.splitext(filename)[0]
        filename = f"{base_name}.{ext}"
    return f"images/partner_card/{filename}"


def blog_image_upload_path(instance, filename):
    """Generate upload path for blog images - uses slug to prevent duplicates"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Use blog slug as filename to prevent duplicates
    if instance.slug:
        filename = f"{instance.slug}.{ext}"
    elif instance.pk:
        filename = f"blog_{instance.pk}.{ext}"
    else:
        base_name = os.path.splitext(filename)[0]
        filename = f"{base_name}.{ext}"
    return f"images/blogs/{filename}"






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


class PartnerComment(models.Model):
    """Model for storing comments on partner posts"""
    partner = models.ForeignKey('Partner', on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    comment_text = models.TextField()
    save_info = models.BooleanField(default=False, help_text='Save name, email for next time')
    is_approved = models.BooleanField(default=False, help_text='Comment is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['partner', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.partner.title}"


class PartnerCommentReply(models.Model):
    """Model for storing replies to partner comments"""
    comment = models.ForeignKey(PartnerComment, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', help_text='Parent reply if this is a nested reply')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    reply_text = models.TextField()
    is_approved = models.BooleanField(default=False, help_text='Reply is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['comment', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author_name} to comment {self.comment.id}"


class Blog(models.Model):
    """Blog model for storing blog posts"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=300, help_text="Blog post title")
    slug = models.SlugField(max_length=300, unique=True, blank=True, help_text="URL-friendly name (auto-generated from title if left blank)")
    author = models.CharField(max_length=100, default="AccessAdvisr", help_text="Author name")
    content = models.TextField(help_text="Full blog post content (HTML supported)")
    image = models.ImageField(upload_to=blog_image_upload_path, blank=True, null=True, help_text="Blog featured image")
    video_url = models.URLField(blank=True, help_text="YouTube video URL")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', help_text="Blog status")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided and handle image cleanup"""
        # Store old image path before saving
        old_image_path = None
        if self.pk:
            try:
                old_blog = Blog.objects.get(pk=self.pk)
                old_image_path = old_blog.image.path if old_blog.image else None
            except Blog.DoesNotExist:
                pass
        
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Blog.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Save first to get the slug
        super().save(*args, **kwargs)
        
        # If image was updated/removed, delete old image file
        if old_image_path:
            current_image_path = self.image.path if (self.image and hasattr(self.image, 'path')) else None
            if old_image_path != current_image_path and os.path.isfile(old_image_path):
                try:
                    os.remove(old_image_path)
                except (OSError, FileNotFoundError):
                    pass
    
    def delete(self, *args, **kwargs):
        """Delete image file when blog is deleted"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL for the blog detail page"""
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def get_comment_count(self):
        """Get count of approved comments"""
        return self.comments.filter(is_approved=True, is_active=True).count()


class BlogComment(models.Model):
    """Model for storing comments on blog posts"""
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    comment_text = models.TextField()
    save_info = models.BooleanField(default=False, help_text='Save name, email for next time')
    is_approved = models.BooleanField(default=False, help_text='Comment is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blog', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.blog.title}"


class BlogCommentReply(models.Model):
    """Model for storing replies to blog comments"""
    comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', help_text='Parent reply if this is a nested reply')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    reply_text = models.TextField()
    is_approved = models.BooleanField(default=False, help_text='Reply is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['comment', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author_name} to comment {self.comment.id}"


class Partner(models.Model):
    """Partner model for storing partner/friend posts"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=300, help_text="Partner post title")
    slug = models.SlugField(max_length=300, unique=True, blank=True, help_text="URL-friendly name (auto-generated from title if left blank)")
    author = models.CharField(max_length=100, default="AccessAdvisr", help_text="Author name")
    image = models.ImageField(upload_to=partner_image_upload_path, blank=True, null=True, help_text="Partner logo/image for card")
    short_description = models.TextField(blank=True, help_text="Short description for card view")
    
    # Video
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    
    # Partner Spotlight Section
    partner_spotlight_title = models.CharField(max_length=300, blank=True, help_text="Partner Spotlight heading")
    partner_spotlight_description = models.TextField(blank=True, help_text="Partner Spotlight description")
    
    # Why AccessAdvisr Partners Section
    why_partner_title = models.CharField(max_length=300, blank=True, help_text="Why AccessAdvisr Partners heading")
    why_partner_description = models.TextField(blank=True, help_text="Why AccessAdvisr Partners description")
    
    # Services Section
    services_title = models.CharField(max_length=300, blank=True, default="Services", help_text="Services section title")
    services_description = models.TextField(blank=True, help_text="Services list (one per line or formatted text)")
    
    # Why Partner Supports AccessAdvisr Section
    why_supports_title = models.CharField(max_length=300, blank=True, help_text="Why Partner Supports AccessAdvisr heading")
    why_supports_description = models.TextField(blank=True, help_text="Why Partner Supports AccessAdvisr description")
    
    # Connect Section
    connect_title = models.CharField(max_length=300, blank=True, help_text="Connect section title")
    connect_description = models.TextField(blank=True, help_text="Connect section description")
    website_url = models.URLField(blank=True, help_text="Official website URL")
    
    # Full Content (for blog-like posts)
    content = models.TextField(blank=True, help_text="Full partner post content (HTML supported)")
    
    # Status and ordering
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', help_text="Partner post status")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'order']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided and handle image cleanup"""
        # Store old image path before saving
        old_image_path = None
        if self.pk:
            try:
                old_partner = Partner.objects.get(pk=self.pk)
                old_image_path = old_partner.image.path if old_partner.image else None
            except Partner.DoesNotExist:
                pass
        
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Partner.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Save first to get the slug
        super().save(*args, **kwargs)
        
        # If image was updated/removed, delete old image file
        if old_image_path:
            current_image_path = self.image.path if (self.image and hasattr(self.image, 'path')) else None
            if old_image_path != current_image_path and os.path.isfile(old_image_path):
                try:
                    os.remove(old_image_path)
                except (OSError, FileNotFoundError):
                    pass
    
    def delete(self, *args, **kwargs):
        """Delete image file when partner is deleted"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL for the partner detail page"""
        from django.urls import reverse
        return reverse('partner_detail', kwargs={'slug': self.slug})
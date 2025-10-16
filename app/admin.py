from django.contrib import admin
from django import forms
from .models import *
from django_ckeditor_5.widgets import CKEditor5Widget

# Change admin site branding
admin.site.site_header = "DIGITAL PRO"
admin.site.site_title = "Marketing Admin Portal"
admin.site.index_title = "Welcome to Marketing Admin Portal"



# ----------------------------
# BlogPost Admin Form
# ----------------------------
class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(config_name='extends'),  # Use CKEditor5 widget
        }

# ----------------------------
# Category Admin
# ----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

# ----------------------------
# Tag Admin
# ----------------------------
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

# ----------------------------
# BlogPost Admin
# ----------------------------
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm
    list_display = ['title', 'category', 'author', 'status', 'is_featured', 'published_at', 'views']
    list_filter = ['status', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'category', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_url')
        }),
        ('Settings', {
            'fields': ('status', 'is_featured', 'read_time', 'author')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Automatically set author if not assigned
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

# ----------------------------
# Contact Admin
# ----------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['fullname', 'email', 'mobile', 'subject', 'created_at']
    search_fields = ['fullname', 'email', 'subject', 'message']
    readonly_fields = ['fullname', 'email', 'mobile', 'subject', 'message', 'created_at']
    ordering = ['-created_at']
    list_filter = ['created_at']

@admin.register(JobRequirement)
class JobRequirementAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "location", "is_active", "posted_on")
    list_filter = ("is_active", "department", "location")
    search_fields = ("title", "department", "location")
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')},
    }


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "job", "applied_on")
    list_filter = ("job",)
    search_fields = ("full_name", "email", "job__title")


@admin.register(OpenApplication)
class OpenApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "desired_position", "submitted_on")
    search_fields = ("full_name", "email", "desired_position")
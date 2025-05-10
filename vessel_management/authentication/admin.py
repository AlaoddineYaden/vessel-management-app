from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('profile_picture', 'profile_picture_preview', 'date_of_birth', 'address', 
              'emergency_contact', 'emergency_phone', 'position', 'joining_date')
    readonly_fields = ('profile_picture_preview',)

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="150" height="150" style="object-fit: cover;"/>', 
                             obj.profile_picture.url)
        return "No profile picture"
    profile_picture_preview.short_description = 'Profile Picture Preview'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined', 'profile_picture_preview')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    list_per_page = 20
    
    def profile_picture_preview(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', 
                             obj.profile.profile_picture.url)
        return "No picture"
    profile_picture_preview.short_description = 'Profile Picture'
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )

admin.site.register(User, CustomUserAdmin)




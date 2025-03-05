from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount

# Register your UserAccount model with UserAdmin
@admin.register(UserAccount)
class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the admin panel
    list_display = ('email','id', 'name', 'phone','bio', 'age', 'photo', 'description','is_active', 'is_staff')

    # Define the fields to filter by in the admin panel
    list_filter = ('is_active', 'is_staff')

    # Define the fieldsets for the add and change forms in the admin panel
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone','bio', 'age', 'photo', 'description',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )

    # Define the fieldsets for the add form in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','id', 'name','phone','bio', 'age', 'photo', 'description', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    # Set the ordering of objects in the admin panel
    ordering = ('is_staff','email',)

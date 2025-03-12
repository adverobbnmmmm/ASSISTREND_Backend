from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount

# Register your UserAccount model with UserAdmin
@admin.register(UserAccount)
class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the admin panel
    list_display = ('id','email', 'name', 'phone','bio','dob','gender','profilepicture', 'description','aim','interest','is_active', 'is_staff','is_blocked')

    # Define the fields to filter by in the admin panel
    list_filter = ('is_active', 'is_staff')

    # Define the fieldsets for the add and change forms in the admin panel
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone','bio','dob','gender','profilepicture', 'description','aim','interest')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )

    # Define the fieldsets for the add form in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name','phone','bio','dob','gender','profilepicture', 'description','aim','interest', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    # Set the ordering of objects in the admin panel
    ordering = ('is_staff','email',)

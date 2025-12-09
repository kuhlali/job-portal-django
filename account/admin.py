from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, OutgoingEmail, DomesticWorker, DomesticJob
from django.utils.html import format_html
from django.core.mail import send_mail


class AddUserForm(forms.ModelForm):
    """
    New User Form. Requires password confirmation.
    """
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirm password', widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'gender', 'role', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UpdateUserForm(forms.ModelForm):
    """
    Update User Form. Doesn't allow changing password in the Admin.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'email', 'password', 'first_name', 'gender', 'role', 'last_name', 'is_active',
            'is_staff'
        )

    def clean_password(self):
# Password can't be changed in the admin
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UpdateUserForm
    add_form = AddUserForm

    list_display = ('email', 'first_name', 'last_name', 'gender', 'role', 'is_staff')
    list_filter = ('is_staff', )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender', 'role', )}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email', 'first_name', 'last_name', 'gender', 'role', 'password1',
                    'password2'
                )
            }
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'first_name', 'last_name')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(DomesticWorker)
admin.site.register(DomesticJob)

# Register OutgoingEmail so sent emails can be viewed in the admin
@admin.register(OutgoingEmail)
class OutgoingEmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to_emails', 'from_email', 'sent', 'created_at')
    list_filter = ('sent', 'created_at')
    search_fields = ('subject', 'to_emails')
    readonly_fields = ('subject', 'body_preview', 'to_emails', 'from_email', 'created_at')
    actions = ['resend_selected_emails']

    def body_preview(self, obj):
        # Show a readable preformatted preview; don't auto-escape so links are visible
        return format_html('<pre style="white-space:pre-wrap;">{}</pre>', obj.body)
    body_preview.short_description = 'Body (preview)'

    def resend_selected_emails(self, request, queryset):
        """Admin action to resend selected stored emails using Django's send_mail.
        Marks the original message `sent=True` if sending succeeds.
        """
        sent_count = 0
        for email in queryset:
            to_list = [e.strip() for e in (email.to_emails or '').split(',') if e.strip()]
            if not to_list:
                continue
            try:
                res = send_mail(email.subject, email.body, email.from_email or None, to_list)
                if res:
                    email.sent = True
                    email.save(update_fields=['sent'])
                    sent_count += 1
            except Exception:
                # ignore per-email failures; admin will see error in logs
                pass

        self.message_user(request, f"Resent {sent_count} emails.")
    resend_selected_emails.short_description = 'Resend selected outgoing emails'
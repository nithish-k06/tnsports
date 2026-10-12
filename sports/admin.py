from django.contrib import admin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import (
    Sport, PlatformStat, District, DistrictTopSport, Coach, Article,
    NewsUpdate, PortalConfig, MinisterControlSetting, Club, DistrictSportsOfficer,
    Tournament, ContactMessage, Athlete, Zone, DistrictSubZone, DistrictPlace,
    StateSportsPlan, MinisterDSOOrder, DSOTransferLog, DSOTransferRequest
)

User = get_user_model()

# ==============================================================================
# 1. TOP BRANDING & SITE CONFIGURATION
# ==============================================================================
admin.site.site_header = "Tamil Nadu Sports Development Platform"
admin.site.site_title = "TN Sports Admin Portal"
admin.site.index_title = "Platform Management Dashboard"


# ==============================================================================
# 2. USER & AUTHENTICATION MANAGEMENT
# ==============================================================================
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Enhanced User admin allowing authorized administrators to view, add, edit,
    activate, and deactivate accounts while preserving Django's built-in permissions and groups.
    """
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_superuser', 'date_joined'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    actions = ['activate_users', 'deactivate_users']

    @admin.action(description="Activate selected user accounts")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user account(s) successfully activated.")

    @admin.action(description="Deactivate selected user accounts")
    def deactivate_users(self, request, queryset):
        if request.user in queryset:
            self.message_user(
                request,
                "Action blocked: You cannot deactivate your currently logged-in account.",
                level=messages.ERROR
            )
            return
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user account(s) successfully deactivated.")


# ==============================================================================
# 3. EXECUTIVE & SYSTEM SETTINGS
# ==============================================================================
@admin.register(MinisterControlSetting)
class MinisterControlSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'total_districts', 'budget_allocation_cr', 'tournament_sanction_mode', 'updated_at')
    fieldsets = (
        ('Statewide Metric Keys', {
            'fields': ('total_districts', 'target_schools', 'verified_pets', 'budget_allocation_cr', 'target_athletes')
        }),
        ('4-Zone Performance Allocations', {
            'fields': (
                ('north_gold_medals', 'north_hq', 'north_districts'),
                ('west_gold_medals', 'west_hq', 'west_districts'),
                ('central_gold_medals', 'central_hq', 'central_districts'),
                ('south_gold_medals', 'south_hq', 'south_districts'),
            )
        }),
        ('Policy & Governance Flags', {
            'fields': ('auto_verify_pet_emis', 'tournament_sanction_mode', 'cm_trophy_registration_open', 'maintenance_mode')
        }),
        ('Role Visibility & Access Control Flags', {
            'fields': (
                ('dso_can_view_statewide_rankings', 'dso_can_view_transfer_history'),
                ('dso_can_edit_subzones', 'coach_can_view_athlete_contacts'),
                ('pet_can_verify_squads', 'public_can_view_leaderboard'),
                ('public_can_view_tournaments', 'public_can_view_coach_directory'),
            )
        }),
        ('Leaderboard Points Weightage', {
            'fields': ('gold_medal_pts', 'silver_medal_pts', 'bronze_medal_pts', 'participation_bonus_pts')
        }),
        ('Executive Announcements & Live Ticker', {
            'fields': ('state_announcement_title', 'state_announcement_body', 'portal_live_ticker')
        }),
        ('Statewide Implementation Plan 2026-2030', {
            'fields': (
                'implementation_plan_title', 'implementation_plan_summary',
                ('implementation_plan_target_year', 'implementation_plan_budget_cr', 'implementation_plan_progress_percent'),
                'implementation_plan_status', 'implementation_plan_image', 'implementation_plan_secondary_image'
            )
        }),
    )


@admin.register(PortalConfig)
class PortalConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'vision_text', 'mission_text')


# ==============================================================================
# 4. SPORTS, ZONES & DISTRICTS
# ==============================================================================
@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'color_badge', 'is_popular', 'order')
    list_filter = ('is_popular', 'category')
    search_fields = ('name', 'category')
    list_editable = ('is_popular', 'order')
    prepopulated_fields = {'slug': ('name',)}

    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; width: 14px; height: 14px; display: inline-block; border-radius: 50%; margin-right: 6px; vertical-align: middle; border: 1px solid rgba(0,0,0,0.1);"></span>{}',
            obj.color or '#16a34a',
            obj.color or '#16a34a'
        )
    color_badge.short_description = "Color"


@admin.register(PlatformStat)
class PlatformStatAdmin(admin.ModelAdmin):
    list_display = ('label', 'count_display', 'icon_class', 'order')
    list_editable = ('count_display', 'order')
    ordering = ('order',)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'headquarters', 'gold_medals_target', 'order')
    list_editable = ('headquarters', 'gold_medals_target', 'order')
    search_fields = ('name', 'code', 'headquarters')


class DistrictTopSportInline(admin.TabularInline):
    model = DistrictTopSport
    extra = 3
    max_num = 3


class DistrictSubZoneInline(admin.TabularInline):
    model = DistrictSubZone
    extra = 1


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'sports_count', 'athletes_count', 'clubs_count', 'tournaments_count')
    list_filter = ('zone',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [DistrictTopSportInline, DistrictSubZoneInline]


@admin.register(DistrictTopSport)
class DistrictTopSportAdmin(admin.ModelAdmin):
    list_display = ('district', 'rank', 'sport_name')
    list_filter = ('rank', 'district__zone', 'district')
    search_fields = ('district__name', 'sport_name')


@admin.register(DistrictPlace)
class DistrictPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'created_at')
    list_filter = ('district__zone', 'district')
    search_fields = ('name', 'district__name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DistrictSubZone)
class DistrictSubZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'headquarters_or_venue', 'contact_officer_name', 'athletes_count', 'is_active')
    list_filter = ('district__zone', 'district', 'is_active')
    search_fields = ('name', 'district__name', 'contact_officer_name')
    filter_horizontal = ('places',)


# ==============================================================================
# 5. ATHLETES, COACHES & CLUBS
# ==============================================================================
@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'emis_id', 'verification_status', 'gender', 'district', 'primary_sport', 'category', 'skill_level', 'created_at')
    list_filter = ('verification_status', 'gender', 'category', 'skill_level', 'age_category', 'district', 'primary_sport')
    search_fields = ('first_name', 'last_name', 'emis_id', 'phone', 'club_or_school', 'qr_token')
    actions = ['mark_cleared', 'mark_flagged']

    @admin.action(description="Mark selected athletes as CLEARED (Pass Issued)")
    def mark_cleared(self, request, queryset):
        updated = queryset.update(verification_status='CLEARED')
        self.message_user(request, f"{updated} athlete(s) marked as Cleared.")

    @admin.action(description="Mark selected athletes as FLAGGED")
    def mark_flagged(self, request, queryset):
        updated = queryset.update(verification_status='FLAGGED')
        self.message_user(request, f"{updated} athlete(s) marked as Flagged.")


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'district', 'experience_years', 'specialization', 'is_active')
    list_filter = ('sport', 'district', 'is_active')
    search_fields = ('name', 'specialization', 'email', 'phone')
    list_editable = ('is_active',)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_sport', 'district', 'contact_person', 'phone', 'status', 'created_at')
    list_filter = ('status', 'primary_sport', 'district')
    search_fields = ('name', 'registration_number', 'contact_person', 'email')
    actions = ['approve_clubs', 'reject_clubs']

    def approve_clubs(self, request, queryset):
        updated = 0
        for club in queryset:
            if club.status != 'VERIFIED':
                club.status = 'VERIFIED'
                club.save()
                updated += 1
                try:
                    subject = f"Club Registration Approved: {club.name}"
                    message = (
                        f"Dear {club.contact_person},\n\n"
                        f"Your sports club / academy registration for '{club.name}' "
                        f"(Reg No: {club.registration_number}) has been approved by the Tamil Nadu Sports Development Authority.\n\n"
                        f"Your club is now officially listed on the TN Sports Portal as a Verified Club.\n\n"
                        f"Best regards,\nTamil Nadu Sports Development Authority"
                    )
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tnsports.gov.in')
                    send_mail(subject, message, from_email, [club.email], fail_silently=True)
                except Exception:
                    pass
        self.message_user(request, f"{updated} club(s) successfully verified and approval notifications sent.")
    approve_clubs.short_description = "Approve selected clubs (Sends Notification Email)"

    def reject_clubs(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, f"{updated} club(s) marked as rejected.")
    reject_clubs.short_description = "Mark selected clubs as rejected"


# ==============================================================================
# 6. DISTRICT SPORTS OFFICERS, TRANSFERS & ORDERS
# ==============================================================================
@admin.register(DistrictSportsOfficer)
class DistrictSportsOfficerAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'zone', 'phone_number', 'official_email', 'is_active')
    list_filter = ('zone', 'is_active')
    search_fields = ('name', 'district__name', 'official_email')
    list_editable = ('is_active',)


@admin.register(DSOTransferLog)
class DSOTransferLogAdmin(admin.ModelAdmin):
    list_display = ('officer', 'from_district', 'to_district', 'go_reference', 'effective_date', 'transferred_at')
    list_filter = ('effective_date', 'transferred_at')
    search_fields = ('officer__name', 'go_reference', 'reason')
    readonly_fields = ('transferred_at',)


@admin.register(DSOTransferRequest)
class DSOTransferRequestAdmin(admin.ModelAdmin):
    list_display = ('officer', 'request_type', 'preferred_district', 'status', 'submitted_at', 'processed_at')
    list_filter = ('status', 'request_type', 'submitted_at')
    search_fields = ('officer__name', 'reason', 'minister_remarks')
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description="Approve selected DSO transfer requests")
    def approve_requests(self, request, queryset):
        updated = queryset.update(status='APPROVED', processed_at=timezone.now())
        self.message_user(request, f"{updated} transfer request(s) approved.")

    @admin.action(description="Reject selected DSO transfer requests")
    def reject_requests(self, request, queryset):
        updated = queryset.update(status='REJECTED', processed_at=timezone.now())
        self.message_user(request, f"{updated} transfer request(s) rejected.")


@admin.register(StateSportsPlan)
class StateSportsPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_code', 'title', 'action_type', 'budget_allocated', 'status', 'progress_percentage', 'created_at')
    list_filter = ('action_type', 'status', 'category')
    search_fields = ('title', 'plan_code', 'existing_plan_name', 'objectives')


@admin.register(MinisterDSOOrder)
class MinisterDSOOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_type', 'title', 'dso', 'district', 'priority', 'status', 'issued_at')
    list_filter = ('order_type', 'priority', 'status', 'district')
    search_fields = ('order_number', 'title', 'instruction')


# ==============================================================================
# 7. TOURNAMENTS, NEWS & COMMUNICATIONS
# ==============================================================================
@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'sport', 'district', 'level_category', 'organizer_name', 'start_date', 'status')
    list_filter = ('status', 'level_category', 'sport', 'district')
    search_fields = ('title', 'organizer_name', 'venue_name')
    actions = ['approve_tournaments', 'reject_tournaments']

    @admin.action(description="Approve selected tournaments")
    def approve_tournaments(self, request, queryset):
        updated = queryset.update(status='APPROVED')
        self.message_user(request, f"{updated} tournament(s) approved.")

    @admin.action(description="Reject selected tournaments")
    def reject_tournaments(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, f"{updated} tournament(s) rejected.")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'is_published')
    list_filter = ('is_published', 'published_date')
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)


@admin.register(NewsUpdate)
class NewsUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience_target', 'date', 'is_active')
    list_filter = ('audience_target', 'is_active', 'date')
    search_fields = ('title', 'summary')
    list_editable = ('audience_target', 'is_active')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_resolved', 'submitted_at')
    list_filter = ('is_resolved', 'submitted_at')
    search_fields = ('name', 'email', 'phone', 'message')
    list_editable = ('is_resolved',)
    actions = ['mark_resolved', 'mark_unresolved']

    @admin.action(description="Mark selected messages as Resolved")
    def mark_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f"{updated} message(s) marked as resolved.")

    @admin.action(description="Mark selected messages as Unresolved")
    def mark_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False)
        self.message_user(request, f"{updated} message(s) marked as unresolved.")
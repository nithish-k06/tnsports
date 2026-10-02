from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Sport(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="Team Sports", help_text="e.g. Team Sports, Individual Sports, Racket Sports, Water Sports")
    icon_class = models.CharField(max_length=50, help_text="Bootstrap or FontAwesome icon class")
    logo_url = models.CharField(max_length=500, blank=True, null=True, help_text="Official sport logo image URL")
    description = models.TextField(blank=True, null=True, help_text="Overview of sport governance and district presence")
    color = models.CharField(max_length=20, default="#16a34a", help_text="Hex code for icon color")
    slug = models.SlugField(max_length=60, blank=True, null=True)
    is_popular = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_popular']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PlatformStat(models.Model):
    label = models.CharField(max_length=50)
    count_display = models.CharField(max_length=20)
    icon_class = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f"{self.count_display} {self.label}"

class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    image_url = models.CharField(max_length=500, blank=True, null=True, help_text="Image URL or thumbnail path")
    published_date = models.DateField()
    summary = models.TextField(help_text="Short introductory summary (1-2 sentences)")
    content = models.TextField(help_text="Full article body content")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_date']
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['published_date']),
            models.Index(fields=['is_published']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Zone(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, help_text="e.g. NORTH, WEST, CENTRAL, SOUTH")
    headquarters = models.CharField(max_length=150, default="District Stadium Complex")
    gold_medals_target = models.PositiveIntegerField(default=40)
    color = models.CharField(max_length=20, default="#2563eb", help_text="Hex code or theme color")
    bg_gradient = models.CharField(max_length=100, default="from-blue-600 to-indigo-700", help_text="Tailwind CSS gradient class string")
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return self.name


class District(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name='districts')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    sports_count = models.PositiveIntegerField(default=25)
    athletes_count = models.PositiveIntegerField(default=120)
    clubs_count = models.PositiveIntegerField(default=18)
    tournaments_count = models.PositiveIntegerField(default=8)
    svg_path_id = models.CharField(max_length=50, blank=True, null=True, help_text="SVG Path element ID on state map")
    svg_region_id = models.CharField(max_length=50, blank=True, null=True, help_text="Links to SVG map path element ID")
    svg_district_id = models.CharField(max_length=50, blank=True, null=True, help_text="Matches SVG path ID (e.g. TN-CO, TN-CH)")

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['zone']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.svg_district_id:
            if self.svg_region_id:
                self.svg_district_id = self.svg_region_id
            elif self.svg_path_id:
                self.svg_district_id = self.svg_path_id
        if not self.svg_region_id:
            self.svg_region_id = self.svg_district_id
        if not self.svg_path_id:
            self.svg_path_id = self.svg_district_id
        super().save(*args, **kwargs)

    @property
    def sports(self):
        return self.sports_count

    @property
    def athletes(self):
        return self.athletes_count

    @property
    def clubs(self):
        return self.clubs_count

    @property
    def tournaments(self):
        return self.tournaments_count

    def __str__(self):
        return self.name



class DistrictTopSport(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='top_sports')
    rank = models.PositiveSmallIntegerField(default=1)
    sport_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['rank']
        unique_together = ['district', 'rank']
        indexes = [
            models.Index(fields=['district', 'rank']),
        ]

    def __str__(self):
        return f"{self.district.name} - #{self.rank} {self.sport_name}"

# Alias for TopSport
TopSport = DistrictTopSport


class DistrictPlace(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=120, help_text="Place, Taluk, Block, or Area Name")
    slug = models.SlugField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['district', 'name']
        verbose_name = "District Place / Taluk"
        verbose_name_plural = "District Places / Taluks"
        indexes = [
            models.Index(fields=['district', 'slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.district.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class DistrictSubZone(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='sub_zones')
    name = models.CharField(max_length=120, help_text="e.g. Madurai Urban Sub-Zone, Coimbatore North Sub-Zone")
    slug = models.SlugField(max_length=150, blank=True)
    headquarters_or_venue = models.CharField(max_length=200, blank=True, help_text="Sub-Zone Stadium or Office Venue")
    covered_places = models.TextField(blank=True, null=True, help_text="Covered places, taluks, or local areas summary")
    places = models.ManyToManyField(DistrictPlace, blank=True, related_name='sub_zones', help_text="Selectable places under this sub-zone")
    contact_officer_name = models.CharField(max_length=100, blank=True, help_text="Sub-Zone Officer or Coordinator Name")
    contact_phone = models.CharField(max_length=20, blank=True)
    athletes_count = models.PositiveIntegerField(default=0)
    clubs_count = models.PositiveIntegerField(default=0)
    schools_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['district', 'name']
        verbose_name = "District Sub-Zone"
        verbose_name_plural = "District Sub-Zones"
        indexes = [
            models.Index(fields=['district', 'slug']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.district.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.district.name})"




class NewsUpdate(models.Model):
    AUDIENCE_CHOICES = (
        ('ALL', 'All'),
        ('PLAYER', 'Players'),
        ('COACH', 'Coaches'),
        ('OFFICER', 'Officers'),
    )
    title = models.CharField(max_length=200)
    summary = models.TextField()
    date = models.DateField(auto_now_add=True)
    audience_target = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='ALL')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = "News Update"
        verbose_name_plural = "News Updates"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['audience_target']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"[{self.get_audience_target_display()}] {self.title}"


class PortalConfig(models.Model):
    vision_text = models.TextField(help_text="Vision statement for the platform")
    mission_text = models.TextField(help_text="Mission statement for the platform")
    banner_image = models.ImageField(upload_to='portal/', blank=True, null=True)
    stadium_image_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        default="https://images.unsplash.com/photo-1577223625816-7546f13df25d?q=80&w=1200&auto=format&fit=crop",
        help_text="URL for stadium or headquarters photo"
    )

    class Meta:
        verbose_name = "Portal Configuration"
        verbose_name_plural = "Portal Configuration"

    def __str__(self):
        return "Tamil Nadu Sports Portal Configuration"


class MinisterControlSetting(models.Model):
    SANCTION_CHOICES = [
        ('AUTO', 'Auto Sanction Tournaments'),
        ('OFFICER_REVIEW', 'DSO Officer Review Required'),
        ('MINISTER_SIGNOFF', 'Sports Minister Approval Required'),
    ]

    # Statewide Key Metrics
    total_districts = models.PositiveIntegerField(default=38, help_text="Total Districts Managed")
    target_schools = models.PositiveIntegerField(default=4120, help_text="Active State Schools")
    verified_pets = models.PositiveIntegerField(default=3840, help_text="Verified PET Teachers")
    budget_allocation_cr = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, help_text="State Budget Allocation (₹ in Crores)")
    target_athletes = models.PositiveIntegerField(default=15000, help_text="Target Athlete Registrations")

    # 4-Zone Performance Allocations
    north_gold_medals = models.PositiveIntegerField(default=42)
    north_hq = models.CharField(max_length=150, default="Chennai Complex")
    north_districts = models.PositiveIntegerField(default=9)

    west_gold_medals = models.PositiveIntegerField(default=48)
    west_hq = models.CharField(max_length=150, default="Coimbatore Complex")
    west_districts = models.PositiveIntegerField(default=10)

    central_gold_medals = models.PositiveIntegerField(default=36)
    central_hq = models.CharField(max_length=150, default="Tiruchirappalli Complex")
    central_districts = models.PositiveIntegerField(default=9)

    south_gold_medals = models.PositiveIntegerField(default=39)
    south_hq = models.CharField(max_length=150, default="Madurai Complex")
    south_districts = models.PositiveIntegerField(default=10)

    # Policy & Governance Flags
    auto_verify_pet_emis = models.BooleanField(default=True, help_text="Enable Automatic PET EMIS Verification")
    tournament_sanction_mode = models.CharField(max_length=25, choices=SANCTION_CHOICES, default='OFFICER_REVIEW')
    cm_trophy_registration_open = models.BooleanField(default=True, help_text="CM Trophy Registrations Active")
    maintenance_mode = models.BooleanField(default=False, help_text="Portal Maintenance Mode Flag")

    # Role Visibility & Module Access Controls (Managed by Sports Minister)
    dso_can_view_statewide_rankings = models.BooleanField(default=True, help_text="Allow DSOs to view statewide leaderboard & analytics")
    dso_can_view_transfer_history = models.BooleanField(default=True, help_text="Allow DSOs to view full transfer audit log")
    dso_can_edit_subzones = models.BooleanField(default=True, help_text="Allow DSOs to manage district sub-zones & taluks")
    coach_can_view_athlete_contacts = models.BooleanField(default=False, help_text="Allow coaches to view athlete personal contact details")
    pet_can_verify_squads = models.BooleanField(default=True, help_text="Allow PET teachers to authorize EMIS student selection squads")
    public_can_view_leaderboard = models.BooleanField(default=True, help_text="Allow public to view district standings")
    public_can_view_tournaments = models.BooleanField(default=True, help_text="Allow public to view sanctioned tournaments")
    public_can_view_coach_directory = models.BooleanField(default=True, help_text="Allow public to search state certified coach directory")

    # Leaderboard Weightage Points
    gold_medal_pts = models.PositiveIntegerField(default=50, help_text="Points per Gold Medal")
    silver_medal_pts = models.PositiveIntegerField(default=30, help_text="Points per Silver Medal")
    bronze_medal_pts = models.PositiveIntegerField(default=10, help_text="Points per Bronze Medal")
    participation_bonus_pts = models.PositiveIntegerField(default=5, help_text="Bonus points per district participant")

    # Executive Announcements & Ticker
    state_announcement_title = models.CharField(max_length=255, default="TN Sports Policy 2026: Executive Infrastructure Sanction", blank=True)
    state_announcement_body = models.TextField(default="₹50 Cr State Budget allocated for rural stadium upgrade, synthetic track installation, and high-performance athlete scholarships.", blank=True)
    portal_live_ticker = models.CharField(max_length=300, default="Welcome to Tamil Nadu Sports Development Authority Portal • Chief Minister Trophy 2026 District Trials Open • Verify PET & School Credentials.", blank=True)

    # Implementation Plan
    implementation_plan_title = models.CharField(max_length=255, default="Statewide Sports Infrastructure & High-Performance Implementation Plan 2026-2030", blank=True)
    implementation_plan_summary = models.TextField(default="Comprehensive 4-Phase Executive Roadmap for Olympic-Grade Synthetic Track Upgrades, 38 District Sports Academies, Biomechanical Science Hubs, & Grassroots Athlete Pipeline.", blank=True)
    implementation_plan_target_year = models.CharField(max_length=50, default="2026 - 2030", blank=True)
    implementation_plan_budget_cr = models.DecimalField(max_digits=10, decimal_places=2, default=250.0, help_text="Total Approved Implementation Budget (₹ Cr)")
    implementation_plan_progress_percent = models.PositiveIntegerField(default=68, help_text="Overall Plan Completion %")
    implementation_plan_status = models.CharField(max_length=100, default="Phase 2 Execution Active", blank=True)
    implementation_plan_image = models.CharField(max_length=500, default="/static/images/minister_masterplan.png", blank=True)
    implementation_plan_secondary_image = models.CharField(max_length=500, default="/static/images/minister_academy_plan.png", blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Minister Executive Control Setting"
        verbose_name_plural = "Minister Executive Control Settings"

    def __str__(self):
        return f"Sports Minister Control Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else 'Initial'})"

    @classmethod
    def get_settings(cls):
        setting, _ = cls.objects.get_or_create(id=1)
        return setting



class Coach(models.Model):
    name = models.CharField(max_length=120)
    photo = models.ImageField(upload_to='coaches/', default='coaches/default.png', blank=True, null=True)
    photo_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Direct URL for coach avatar image fallback"
    )
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='coaches')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='coaches')
    experience_years = models.PositiveIntegerField(default=5)
    specialization = models.CharField(max_length=120, help_text="e.g. Batting, Defense, Sprint, Coaching, Goal Keeper")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-experience_years', 'name']
        verbose_name = "Coach"
        verbose_name_plural = "Coaches"
        indexes = [
            models.Index(fields=['district', 'sport']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sport.name} - {self.district.name})"


class Club(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]

    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    registration_number = models.CharField(max_length=60, unique=True, help_text="Society / Trust / Association Reg. No.")
    established_year = models.PositiveIntegerField()
    primary_sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='clubs')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='clubs')
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    logo = models.ImageField(upload_to='club_logos/', default='club_logos/default.png', blank=True)
    reg_certificate = models.FileField(upload_to='club_certificates/', blank=True, null=True)
    total_members = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['district', 'primary_sport']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DistrictSportsOfficer(models.Model):
    ZONE_CHOICES = [
        ('NORTH', 'North Zone'),
        ('SOUTH', 'South Zone'),
        ('WEST', 'West Zone'),
        ('CENTRAL', 'Central Zone'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dso_profile', null=True, blank=True)
    name = models.CharField(max_length=120)
    designation = models.CharField(max_length=100, default="District Sports & Youth Welfare Officer")
    district = models.OneToOneField(District, on_delete=models.CASCADE, related_name='officer')
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, default='CENTRAL')
    office_address = models.TextField(help_text="e.g., SDAT District Stadium Complex")
    official_email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='officers/', default='officers/default.png', blank=True, null=True)
    photo_url = models.CharField(max_length=500, blank=True, null=True, help_text="Fallback photo URL")
    appointed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['district__name']
        verbose_name = "District Sports Officer"
        verbose_name_plural = "District Sports Officers"
        indexes = [
            models.Index(fields=['district']),
            models.Index(fields=['zone']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - DSO ({self.district.name})"


class StateSportsPlan(models.Model):
    ACTION_CHOICES = [
        ('NEW_PLAN', 'New State Plan Implementation'),
        ('UPGRADE_PLAN', 'Upgrade Existing Plan'),
    ]

    STATUS_CHOICES = [
        ('PROPOSED', 'Proposed Plan'),
        ('SANCTIONED', 'Sanctioned by Minister'),
        ('IN_PROGRESS', 'Implementation Underway'),
        ('COMPLETED', 'Fully Implemented Across State'),
    ]

    title = models.CharField(max_length=255, help_text="Scheme / Plan Title, e.g. CM Trophy Talent Excellence Scheme 2026")
    plan_code = models.CharField(max_length=50, unique=True, help_text="e.g. TN-SP-2026-001")
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default='NEW_PLAN')
    category = models.CharField(max_length=100, default="Infrastructure & Talent", help_text="e.g. Infrastructure, Grassroots Talent, Athlete Support")
    existing_plan_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of existing plan if upgrading")
    budget_allocated = models.CharField(max_length=100, default="₹15 Crores", help_text="Budget Allocation string")
    target_districts_count = models.PositiveIntegerField(default=38, help_text="Number of target districts")
    objectives = models.TextField(help_text="Key objectives & rollout directives")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SANCTIONED')
    progress_percentage = models.PositiveIntegerField(default=35, help_text="Implementation progress (0-100%)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "State Sports Plan"
        verbose_name_plural = "State Sports Plans"

    def __str__(self):
        return f"[{self.plan_code}] {self.title} ({self.get_action_type_display()})"


class MinisterDSOOrder(models.Model):
    ORDER_TYPE_CHOICES = [
        ('DIRECTIVE', 'General Executive Directive'),
        ('UPGRADE_PLAN', 'Upgrade Existing State Plan'),
        ('NEW_PLAN', 'Implement New State Plan'),
    ]

    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority Directive'),
        ('URGENT', 'Urgent Action Required'),
        ('ROUTINE', 'Routine Directive'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Issued - Awaiting Compliance'),
        ('IN_PROGRESS', 'Compliance Underway'),
        ('COMPLETED', 'Complied & Verified'),
    ]

    order_number = models.CharField(max_length=60, help_text="Government Order Ref, e.g. G.O. Ms. No. 89/2026")
    order_type = models.CharField(max_length=30, choices=ORDER_TYPE_CHOICES, default='DIRECTIVE')
    plan = models.ForeignKey(StateSportsPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    dso = models.ForeignKey(DistrictSportsOfficer, on_delete=models.CASCADE, related_name='minister_orders', null=True, blank=True, help_text="Target DSO (Leave blank for statewide order)")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='minister_orders', null=True, blank=True, help_text="Target District")
    title = models.CharField(max_length=255, help_text="Subject / Directive Title")
    budget_allocated = models.CharField(max_length=100, blank=True, null=True, help_text="Budget allocation e.g. ₹20 Crores")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='HIGH')
    instruction = models.TextField(help_text="Detailed Order text / instruction from Sports Minister")
    target_date = models.DateField(null=True, blank=True, help_text="Compliance deadline")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    compliance_report = models.TextField(blank=True, null=True, help_text="DSO compliance feedback text")
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issued_at']
        verbose_name = "Minister Executive Order to DSO"
        verbose_name_plural = "Minister Executive Orders to DSOs"
        indexes = [
            models.Index(fields=['dso', 'status']),
            models.Index(fields=['issued_at']),
        ]

    def __str__(self):
        target = self.dso.name if self.dso else (self.district.name if self.district else "All DSOs")
        return f"[{self.order_number}] {self.title} -> {target}"


class DSOTransferLog(models.Model):
    officer = models.ForeignKey(DistrictSportsOfficer, on_delete=models.CASCADE, related_name='transfer_history')
    from_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_from')
    to_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_to')
    go_reference = models.CharField(max_length=100, help_text="e.g. G.O. Ms. No. 154/2026 Sports Dept")
    reason = models.TextField(blank=True, null=True, help_text="Transfer Rationale / Reassignment Details")
    effective_date = models.DateField(null=True, blank=True)
    transferred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transferred_at']
        verbose_name = "DSO Transfer Log"
        verbose_name_plural = "DSO Transfer Logs"
        indexes = [
            models.Index(fields=['officer']),
            models.Index(fields=['transferred_at']),
        ]

    def __str__(self):
        from_name = self.from_district.name if self.from_district else "Unassigned"
        to_name = self.to_district.name if self.to_district else "Unassigned"
        return f"{self.officer.name}: {from_name} -> {to_name} ({self.go_reference})"


class DSOTransferRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('TRANSFER', 'District Transfer Request'),
        ('REASSIGNMENT', 'Reassignment / Duty Change Request'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Minister Review'),
        ('APPROVED', 'Approved & Order Issued'),
        ('REJECTED', 'Rejected by Minister'),
    ]

    officer = models.ForeignKey(DistrictSportsOfficer, on_delete=models.CASCADE, related_name='transfer_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='TRANSFER')
    preferred_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='requested_transfers', help_text="Target district if Transfer Request")
    preferred_duty = models.CharField(max_length=255, blank=True, null=True, help_text="Target duty/zone/responsibility if Reassignment Request")
    reason = models.TextField(help_text="Detailed reason / rationale for transfer or reassignment")
    additional_remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    minister_remarks = models.TextField(blank=True, null=True, help_text="Remarks from Sports Minister upon decision")
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "DSO Transfer & Reassignment Request"
        verbose_name_plural = "DSO Transfer & Reassignment Requests"
        indexes = [
            models.Index(fields=['officer', 'status']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        req_type = self.get_request_type_display()
        return f"[{self.status}] {self.officer.name} - {req_type} ({self.submitted_at.strftime('%Y-%m-%d')})"


class Tournament(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending DSO Approval'),
        ('DSO_APPROVED', 'Approved by DSO - Pending Minister News Approval'),
        ('APPROVED', 'Sanctioned & Published in State News'),
        ('REJECTED', 'Rejected'),
    ]

    LEVEL_CHOICES = [
        ('SCHOOL', 'School Level'),
        ('COLLEGE', 'College / University Level'),
        ('GENERAL', 'General / Open Age Level'),
    ]

    title = models.CharField(max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='tournaments')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='tournaments')
    level_category = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='GENERAL', help_text="School, College or General Open Category")
    age_condition = models.CharField(max_length=100, default="Open Category (All Ages)", help_text="e.g. Under 14, Under 17, Under 25, Open 18+, Masters 35+")
    organizer_name = models.CharField(max_length=120)
    organizer_contact = models.CharField(max_length=15)
    organizer_email = models.EmailField()
    venue_name = models.CharField(max_length=200, help_text="e.g., VOC Stadium Ground")
    start_date = models.DateField()
    end_date = models.DateField()
    entry_deadline = models.DateField()
    expected_teams = models.PositiveIntegerField(default=8)
    rulebook_doc = models.FileField(upload_to='tournament_docs/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['district', 'sport']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
        ]

    def __str__(self):
        return f"{self.title} ({self.district.name})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['submitted_at']),
            models.Index(fields=['is_resolved']),
        ]

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class Athlete(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    SKILL_LEVEL_CHOICES = (
        ('BEGINNER', 'Beginner'),
        ('DISTRICT', 'District Level'),
        ('STATE', 'State Level'),
        ('NATIONAL', 'National Level'),
    )

    CATEGORY_CHOICES = (
        ('SCHOOL', 'School Player'),
        ('COLLEGE', 'College Player'),
        ('OPEN', 'Professional / Open'),
    )

    VERIFICATION_STATUS_CHOICES = (
        ('PENDING', 'Pending Verification'),
        ('CLEARED', 'Cleared / Pass Issued'),
        ('FLAGGED', 'Flagged / Disqualified'),
    )

    AGE_CATEGORY_CHOICES = (
        ('U14', 'Under 14'),
        ('U17', 'Under 17'),
        ('U19', 'Under 19'),
        ('OPEN', 'Open Senior'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_profile')
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='athletes')
    primary_sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, related_name='athletes')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='SCHOOL')
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='BEGINNER')
    club_or_school = models.CharField(max_length=150, blank=True)
    emis_id = models.CharField(max_length=20, blank=True, null=True, unique=True, help_text="16-Digit EMIS Student Identifier")
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='CLEARED')
    age_category = models.CharField(max_length=20, choices=AGE_CATEGORY_CHOICES, default='U17')
    qr_token = models.CharField(max_length=64, blank=True, null=True, help_text="Unique QR Token for digital pass")
    id_proof = models.FileField(upload_to='athlete_docs/', blank=True, null=True, help_text="Aadhaar or School ID")
    profile_photo = models.ImageField(upload_to='athlete_photos/', default='default_player.png', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Athlete'
        verbose_name_plural = 'Athletes'
        indexes = [
            models.Index(fields=['district', 'primary_sport']),
            models.Index(fields=['category']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['emis_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.primary_sport.name if self.primary_sport else 'Athlete'})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"





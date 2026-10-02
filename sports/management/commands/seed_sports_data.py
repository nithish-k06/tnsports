from django.core.management.base import BaseCommand
from django.utils.text import slugify
from sports.models import District, Sport, PlatformStat

class Command(BaseCommand):
    help = "Seeds initial sports disciplines, statistics, and all 38 districts of Tamil Nadu."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding Tamil Nadu Sports Platform Data..."))

        # 1. Seed Sports Disciplines
        sports_data = [
            {"name": "Cricket", "category": "Team Sports", "icon_class": "bi bi-slash-lg", "color": "#16a34a", "is_popular": True, "order": 1},
            {"name": "Football", "category": "Team Sports", "icon_class": "bi bi-circle", "color": "#dc2626", "is_popular": True, "order": 2},
            {"name": "Hockey", "category": "Team Sports", "icon_class": "bi bi-person-walking", "color": "#2563eb", "is_popular": True, "order": 3},
            {"name": "Kabaddi", "category": "Team Sports", "icon_class": "bi bi-lightning-charge-fill", "color": "#ea580c", "is_popular": True, "order": 4},
            {"name": "Athletics", "category": "Individual Sports", "icon_class": "bi bi-person-running", "color": "#9333ea", "is_popular": True, "order": 5},
            {"name": "Badminton", "category": "Racket Sports", "icon_class": "bi bi-balloon", "color": "#f59e0b", "is_popular": True, "order": 6},
            {"name": "Volleyball", "category": "Team Sports", "icon_class": "bi bi-disc", "color": "#0284c7", "is_popular": False, "order": 7},
            {"name": "Basketball", "category": "Team Sports", "icon_class": "bi bi-dribbble", "color": "#d97706", "is_popular": False, "order": 8},
            {"name": "Swimming", "category": "Water Sports", "icon_class": "bi bi-water", "color": "#0891b2", "is_popular": False, "order": 9},
            {"name": "Table Tennis", "category": "Racket Sports", "icon_class": "bi bi-award", "color": "#4f46e5", "is_popular": False, "order": 10},
            {"name": "Chess", "category": "Individual Sports", "icon_class": "bi bi-shield", "color": "#7c3aed", "is_popular": False, "order": 11},
            {"name": "Weightlifting", "category": "Individual Sports", "icon_class": "bi bi-box", "color": "#059669", "is_popular": False, "order": 12},
        ]

        sports_created = 0
        for s in sports_data:
            obj, created = Sport.objects.get_or_create(
                name=s["name"],
                defaults={
                    "category": s["category"],
                    "icon_class": s["icon_class"],
                    "color": s["color"],
                    "slug": slugify(s["name"]),
                    "is_popular": s["is_popular"],
                    "order": s["order"]
                }
            )
            if created:
                sports_created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {sports_created} new Sports disciplines."))

        # 2. Seed all 38 Tamil Nadu Districts
        tn_districts = [
            "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
            "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram",
            "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
            "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
            "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
            "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
            "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
            "Vellore", "Viluppuram", "Virudhunagar"
        ]

        districts_created = 0
        for name in tn_districts:
            obj, created = District.objects.get_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "sports_count": 0,
                    "athletes_count": 0,
                    "clubs_count": 0,
                    "tournaments_count": 0,
                }
            )
            if created:
                districts_created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {districts_created} Tamil Nadu Districts (Total in DB: {District.objects.count()})."))

        # 3. Seed Platform Stats
        stats_data = [
            {"label": "Districts", "count_display": "38", "icon_class": "bi bi-bank", "order": 1},
            {"label": "Sports", "count_display": "50+", "icon_class": "bi bi-bullseye", "order": 2},
            {"label": "Players", "count_display": "1000+", "icon_class": "bi bi-person-fill", "order": 3},
            {"label": "Clubs", "count_display": "200+", "icon_class": "bi bi-people-fill", "order": 4},
            {"label": "Tournaments", "count_display": "100+", "icon_class": "bi bi-trophy-fill", "order": 5},
        ]

        for st in stats_data:
            PlatformStat.objects.get_or_create(
                label=st["label"],
                defaults={
                    "count_display": st["count_display"],
                    "icon_class": st["icon_class"],
                    "order": st["order"]
                }
            )

        self.stdout.write(self.style.SUCCESS("Platform stats successfully initialized! All data seeding complete."))

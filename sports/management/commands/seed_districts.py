from django.core.management.base import BaseCommand
from django.utils.text import slugify
from sports.models import District, DistrictTopSport

TAMIL_NADU_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram",
    "Kanniyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivagangai", "Tenkasi",
    "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
    "Vellore", "Viluppuram", "Virudhunagar"
]

DEFAULT_TOP_SPORTS = [
    ("Cricket", 1),
    ("Football", 2),
    ("Athletics", 3)
]

class Command(BaseCommand):
    help = "Populate all 38 Tamil Nadu districts"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding all 38 Tamil Nadu districts..."))
        created_count = 0
        
        for name in TAMIL_NADU_DISTRICTS:
            district_slug = slugify(name)
            district, created = District.objects.get_or_create(
                slug=district_slug,
                defaults={
                    'name': name,
                    'sports_count': 0,
                    'athletes_count': 0,
                    'clubs_count': 0,
                    'tournaments_count': 0,
                }
            )
            if created:
                created_count += 1

            # Ensure Top Sports exist for each district
            if not DistrictTopSport.objects.filter(district=district).exists():
                for sport_name, rank in DEFAULT_TOP_SPORTS:
                    DistrictTopSport.objects.create(
                        district=district,
                        sport_name=sport_name,
                        rank=rank
                    )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded all 38 Tamil Nadu districts! (New created: {created_count}, Total: {District.objects.count()})"))

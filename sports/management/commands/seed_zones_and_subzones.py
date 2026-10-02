from django.core.management.base import BaseCommand
from django.utils.text import slugify
from sports.models import Zone, District, DistrictSubZone, DistrictPlace

ZONES_DATA = [
    {
        'code': 'NORTH',
        'name': 'North Zone',
        'headquarters': 'Chennai Complex',
        'gold_medals_target': 42,
        'color': '#2563eb',
        'bg_gradient': 'from-blue-600 to-indigo-700',
        'order': 1,
        'districts': ["Chennai", "Kanchipuram", "Chengalpattu", "Tiruvallur", "Tiruvannamalai", "Vellore", "Ranipet", "Tirupathur", "Viluppuram"]
    },
    {
        'code': 'WEST',
        'name': 'West Zone',
        'headquarters': 'Coimbatore Complex',
        'gold_medals_target': 48,
        'color': '#16a34a',
        'bg_gradient': 'from-emerald-600 to-teal-700',
        'order': 2,
        'districts': ["Coimbatore", "Nilgiris", "Tiruppur", "Erode", "Salem", "Namakkal", "Dharmapuri", "Krishnagiri", "Karur"]
    },
    {
        'code': 'CENTRAL',
        'name': 'Central Zone',
        'headquarters': 'Tiruchirappalli Complex',
        'gold_medals_target': 36,
        'color': '#ea580c',
        'bg_gradient': 'from-orange-600 to-amber-700',
        'order': 3,
        'districts': ["Tiruchirappalli", "Thanjavur", "Tiruvarur", "Nagapattinam", "Mayiladuthurai", "Perambalur", "Ariyalur", "Pudukkottai", "Kallakurichi", "Cuddalore"]
    },
    {
        'code': 'SOUTH',
        'name': 'South Zone',
        'headquarters': 'Madurai Complex',
        'gold_medals_target': 39,
        'color': '#9333ea',
        'bg_gradient': 'from-purple-600 to-violet-700',
        'order': 4,
        'districts': ["Madurai", "Dindigul", "Theni", "Virudhunagar", "Ramanathapuram", "Sivagangai", "Tirunelveli", "Tenkasi", "Thoothukudi", "Kanniyakumari"]
    }
]

DISTRICT_REAL_PLACES = {
    "Chennai": ["Mylapore", "Anna Nagar", "T. Nagar", "Adyar", "Guindy", "Velachery", "Ambattur", "Royapettah", "Perambur", "Egmore"],
    "Kanchipuram": ["Kanchipuram Urban", "Sriperumbudur", "Walajabad", "Utiramerur", "Kundrathur"],
    "Chengalpattu": ["Chengalpattu Town", "Tambaram", "Pallavaram", "Mahabalipuram", "Madurantakam", "Chromepet"],
    "Tiruvallur": ["Tiruvallur Town", "Avadi", "Ponneri", "Tiruttani", "Gummidipoondi", "Poonamallee"],
    "Tiruvannamalai": ["Tiruvannamalai Town", "Arani", "Cheyyar", "Polur", "Chengam", "Vandavasi"],
    "Vellore": ["Vellore Fort City", "Katpadi", "Gudiyatham", "Anaicut", "Pernambut"],
    "Ranipet": ["Ranipet Urban", "Walajah", "Arcot", "Sholinghur", "Arakkonam"],
    "Tirupathur": ["Tirupathur Town", "Vaniyambadi", "Ambur", "Natrampalli", "Yelagiri Hills"],
    "Viluppuram": ["Viluppuram Town", "Tindivanam", "Gingee", "Vikravandi", "Vanur"],
    "Coimbatore": ["RS Puram", "Peelamedu", "Gandhipuram", "Pollachi", "Mettupalayam", "Saravanampatti", "Thudiyalur", "Kinathukadavu", "Valparai"],
    "Nilgiris": ["Udhagamandalam (Ooty)", "Coonoor", "Kotagiri", "Gudalur", "Pandalur"],
    "Tiruppur": ["Tiruppur North", "Tiruppur South", "Avinashi", "Dharapuram", "Udumalaipettai", "Palladam", "Kangeyam"],
    "Erode": ["Erode Central", "Perundurai", "Gobichettipalayam", "Bhavani", "Sathyamangalam", "Modakurichi"],
    "Salem": ["Salem Urban", "Attur", "Mettur", "Omalur", "Sankari", "Edappadi", "Yercaud"],
    "Namakkal": ["Namakkal Town", "Rasipuram", "Tiruchengodu", "Paramathi Velur", "Kolli Hills"],
    "Dharmapuri": ["Dharmapuri Town", "Harur", "Palacode", "Pennagaram", "Pappireddipatti", "Karimangalam"],
    "Krishnagiri": ["Krishnagiri Town", "Hosur Industrial Complex", "Denkanikottai", "Pochampalli", "Bargur", "Uthangarai"],
    "Karur": ["Karur Town", "Kulithalai", "Aravakurichi", "Manmangalam", "Velayuthampalayam"],
    "Tiruchirappalli": ["Trichy Fort", "Srirangam", "Thiruverumbur", "Lalgudi", "Manapparai", "Musiri", "Thuraiyur"],
    "Thanjavur": ["Thanjavur City", "Kumbakonam", "Pattukkottai", "Orathanadu", "Papanasam", "Thiruvaiyaru"],
    "Tiruvarur": ["Tiruvarur Town", "Mannargudi", "Thiruthuraipoondi", "Nannilam", "Kudavasal"],
    "Nagapattinam": ["Nagapattinam Port", "Velankanni", "Kilvelur", "Vedaranyam", "Thirukkuvalai"],
    "Mayiladuthurai": ["Mayiladuthurai Town", "Sirkazhi", "Poompuhar", "Tharangambadi", "Kuthalam"],
    "Perambalur": ["Perambalur Town", "Kunnam", "Veppanthattai", "Alathur"],
    "Ariyalur": ["Ariyalur Town", "Jayankondam", "Sendurai", "Udayarpalayam"],
    "Pudukkottai": ["Pudukkottai Town", "Aranthangi", "Illuppur", "Alangudi", "Thirumayam", "Gandarvakkottai"],
    "Kallakurichi": ["Kallakurichi Town", "Sankarapuram", "Ulundurpet", "Tirukoilur", "Kalvarayan Hills"],
    "Cuddalore": ["Cuddalore Port", "Chidambaram", "Neyveli", "Panruti", "Vriddhachalam", "Kattumannarkoil"],
    "Madurai": ["Madurai Central (Goripalayam)", "Tallakulam", "Thiruparankundram", "Melur", "Usilampatti", "Vadipatti", "Thirumangalam"],
    "Dindigul": ["Dindigul City", "Palani", "Kodaikanal", "Nilakottai", "Oddanchatram", "Natham"],
    "Theni": ["Theni Town", "Periyakulam", "Bodinayakanur", "Cumbum", "Uthamapalayam"],
    "Virudhunagar": ["Virudhunagar Town", "Sivakasi", "Rajapalayam", "Aruppukottai", "Sattur", "Srivilliputhur"],
    "Ramanathapuram": ["Ramanathapuram Town", "Rameswaram", "Paramakudi", "Mudukulathur", "Keelakarai", "Tiruvadanai"],
    "Sivagangai": ["Sivagangai Town", "Karaikudi", "Devakottai", "Manamadurai", "Tirupathur"],
    "Tirunelveli": ["Tirunelveli City", "Palayamkottai", "Ambasamudram", "Cheranmahadevi", "Nanguneri", "Radhapuram"],
    "Tenkasi": ["Tenkasi Town", "Courtallam", "Sankarankovil", "Kadayanallur", "Puliyangudi", "Shenkottai"],
    "Thoothukudi": ["Thoothukudi Port", "Tiruchendur", "Kovilpatti", "Sattankulam", "Ettayapuram", "Vilathikulam"],
    "Kanniyakumari": ["Nagercoil", "Kanyakumari Beach", "Padmanabhapuram", "Marthandam", "Thuckalay", "Colachel"],
}

class Command(BaseCommand):
    help = "Seed baseline 4 Zones, assign 38 districts to zones, seed authentic Tamil Nadu places and sub-zones."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding authentic Tamil Nadu District Places & Sub-Zones..."))

        total_places_created = 0
        total_subzones_created = 0

        for z_info in ZONES_DATA:
            zone, _ = Zone.objects.get_or_create(
                code=z_info['code'],
                defaults={
                    'name': z_info['name'],
                    'headquarters': z_info['headquarters'],
                    'gold_medals_target': z_info['gold_medals_target'],
                    'color': z_info['color'],
                    'bg_gradient': z_info['bg_gradient'],
                    'order': z_info['order'],
                }
            )

            # Assign districts to zone
            for dist_name in z_info['districts']:
                district, _ = District.objects.get_or_create(
                    slug=slugify(dist_name),
                    defaults={'name': dist_name}
                )
                district.zone = zone
                district.save()

                # Clean up old generic placeholder places for this district
                generic_suffixes = ["City Center", "North Taluk", "South Block", "East Avenue", "West Industrial Sector"]
                for p in list(DistrictPlace.objects.filter(district=district)):
                    if any(p.name.endswith(suf) for suf in generic_suffixes):
                        p.delete()

                # Get real places for this district
                real_places_list = DISTRICT_REAL_PLACES.get(dist_name, [
                    f"{dist_name} Town", f"{dist_name} North", f"{dist_name} South", f"{dist_name} East", f"{dist_name} West"
                ])

                place_objs = []
                for p_name in real_places_list:
                    p_obj, p_created = DistrictPlace.objects.get_or_create(
                        district=district,
                        name=p_name
                    )
                    if p_created:
                        total_places_created += 1
                    place_objs.append(p_obj)

                # Seed/update Sub-Zones per District
                subzones = list(DistrictSubZone.objects.filter(district=district))
                if not subzones:
                    sub_zone_types = [
                        ("Urban Sub-Zone", f"{real_places_list[0]}, {real_places_list[1] if len(real_places_list) > 1 else real_places_list[0]}", "", place_objs[:3]),
                        ("North Sub-Zone", f"{real_places_list[2] if len(real_places_list) > 2 else real_places_list[0]}, {real_places_list[3] if len(real_places_list) > 3 else real_places_list[0]}", "", place_objs[2:5]),
                        ("South-Rural Sub-Zone", f"{real_places_list[-2] if len(real_places_list) > 4 else real_places_list[0]}, {real_places_list[-1]}", "", place_objs[3:])
                    ]
                    for idx, (sz_title, places_summary, officer, p_subset) in enumerate(sub_zone_types, start=1):
                        sz_name = f"{dist_name} {sz_title}"
                        sz_obj = DistrictSubZone.objects.create(
                            district=district,
                            name=sz_name,
                            covered_places=places_summary,
                            contact_officer_name="",
                            contact_phone="",
                            athletes_count=0,
                            clubs_count=0,
                            schools_count=0,
                            is_active=True
                        )
                        sz_obj.places.set(p_subset)
                        total_subzones_created += 1
                else:
                    # Update existing subzones to use real places
                    half = max(1, len(place_objs) // len(subzones))
                    for idx, sz in enumerate(subzones):
                        start_idx = idx * half
                        end_idx = start_idx + half + 1
                        assigned_places = place_objs[start_idx:end_idx] if place_objs[start_idx:end_idx] else place_objs[:2]
                        sz.places.set(assigned_places)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded authentic places for all 38 districts! Total Places: {DistrictPlace.objects.count()} (New: {total_places_created}), Sub-Zones: {DistrictSubZone.objects.count()}."
            )
        )

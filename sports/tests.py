from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from sports.models import Sport, District, DistrictSportsOfficer, Tournament
from sports.forms import TournamentSanctionRequestForm

class TournamentSanctionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sport = Sport.objects.create(name="Football", category="Team Sports")
        self.district = District.objects.create(name="Coimbatore", slug="coimbatore")
        self.user = User.objects.create_user(username="dso_user", password="password123")
        self.dso = DistrictSportsOfficer.objects.create(
            user=self.user,
            name="Test DSO",
            district=self.district,
            official_email="dso.coimbatore@tn.gov.in",
            phone_number="+919876543210"
        )

    def test_tournament_sanction_request_form_valid(self):
        form_data = {
            'title': 'Kovai Premier League 2026',
            'sport': self.sport.id,
            'district': self.district.id,
            'level_category': 'GENERAL',
            'age_condition': 'Open Category (All Ages)',
            'organizer_name': 'Kovai Sports Club',
            'organizer_contact': '+919876543210',
            'organizer_email': 'contact@kovaisports.com',
            'venue_name': 'Nehru Stadium',
            'start_date': '2026-10-01',
            'end_date': '2026-10-05',
            'entry_deadline': '2026-09-25',
            'expected_teams': 16,
        }
        form = TournamentSanctionRequestForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_tournaments_view_post_creates_pending_tournament(self):
        form_data = {
            'title': 'Kongu Trophy Football 2026',
            'sport': self.sport.id,
            'district': self.district.id,
            'level_category': 'GENERAL',
            'age_condition': 'Open Category (All Ages)',
            'organizer_name': 'Kongu FC',
            'organizer_contact': '+919876543210',
            'organizer_email': 'info@kongufc.org',
            'venue_name': 'VOC Ground',
            'start_date': '2026-10-10',
            'end_date': '2026-10-15',
            'entry_deadline': '2026-10-01',
            'expected_teams': 12,
        }
        response = self.client.post(reverse('tournaments'), form_data)
        self.assertEqual(response.status_code, 302)
        
        tournament = Tournament.objects.get(title='Kongu Trophy Football 2026')
        self.assertEqual(tournament.status, 'PENDING')
        self.assertEqual(tournament.district, self.district)

    def test_dso_tournament_approve_action(self):
        tournament = Tournament.objects.create(
            title='District Championship 2026',
            sport=self.sport,
            district=self.district,
            organizer_name='Organizing Body',
            organizer_contact='+919876543210',
            organizer_email='org@test.com',
            venue_name='District Ground',
            start_date='2026-11-01',
            end_date='2026-11-05',
            entry_deadline='2026-10-25',
            status='PENDING'
        )
        self.client.login(username="dso_user", password="password123")
        url = reverse('dso_tournament_action', kwargs={'tournament_id': tournament.id, 'action': 'approve'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        tournament.refresh_from_db()
        self.assertEqual(tournament.status, 'DSO_APPROVED')

    def test_minister_tournament_news_approve_action(self):
        minister_user = User.objects.create_superuser(username="minister_news_user", email="minister_news@tn.gov.in", password="password123")
        tournament = Tournament.objects.create(
            title='CM Trophy Zonal Championship 2026',
            sport=self.sport,
            district=self.district,
            organizer_name='SDAT Executive Body',
            organizer_contact='+919876543210',
            organizer_email='sdat@tn.gov.in',
            venue_name='Nehru Complex',
            start_date='2026-11-10',
            end_date='2026-11-15',
            entry_deadline='2026-11-01',
            status='DSO_APPROVED'
        )
        self.client.login(username="minister_news_user", password="password123")
        url = reverse('minister_tournament_news_action', kwargs={'tournament_id': tournament.id, 'action': 'approve'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        tournament.refresh_from_db()
        self.assertEqual(tournament.status, 'APPROVED')

        from sports.models import NewsUpdate, Article
        self.assertTrue(NewsUpdate.objects.filter(title__contains='CM Trophy Zonal Championship 2026').exists())
        self.assertTrue(Article.objects.filter(title__contains='CM Trophy Zonal Championship 2026').exists())


class CoachRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sport = Sport.objects.create(name="Badminton", category="Racket Sports")
        self.district = District.objects.create(name="Madurai", slug="madurai")

    def test_coach_registration_view_get(self):
        response = self.client.get(reverse('coach_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_register.html')

    def test_coach_registration_view_post_success(self):
        form_data = {
            'name': 'P. Gopichand',
            'email': 'gopichand.badminton@tnsports.gov.in',
            'phone': '+91 98401 99999',
            'sport': self.sport.id,
            'district': self.district.id,
            'experience_years': 18,
            'specialization': 'High Performance Single & Double Tactics',
        }
        response = self.client.post(reverse('coach_register'), form_data)
        self.assertEqual(response.status_code, 302)
        
        from sports.models import Coach
        coach = Coach.objects.get(email='gopichand.badminton@tnsports.gov.in')
        self.assertEqual(coach.name, 'P. Gopichand')
        self.assertEqual(coach.experience_years, 18)
        self.assertTrue(coach.is_active)


class SessionSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_session_user", password="password123")

    def test_session_logout_with_expiration_reason(self):
        self.client.login(username="test_session_user", password="password123")
        response = self.client.get(reverse('logout') + '?reason=session_expired')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_api_session_keepalive_authenticated(self):
        self.client.login(username="test_session_user", password="password123")
        response = self.client.post(reverse('api_session_keepalive'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')


class SportsDirectoryTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_sports_list_view_seeds_and_renders_all_sports_alphabetically(self):
        response = self.client.get(reverse('sports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports.html')
        
        # Verify 26 sports seeded
        self.assertEqual(Sport.objects.count(), 26)

        # Verify strict A-Z alphabetical ordering across all sports
        sport_names = list(Sport.objects.all().values_list('name', flat=True))
        self.assertEqual(sport_names, sorted(sport_names))
        
        # Verify Kho Kho is present in Traditional & Indigenous category with valid logo
        kho_kho = Sport.objects.get(name='Kho Kho')
        self.assertEqual(kho_kho.category, 'Traditional & Indigenous')
        self.assertTrue(kho_kho.logo_url)

        # Check all sports have logos
        for s in Sport.objects.all():
            self.assertTrue(s.logo_url, f"Sport {s.name} is missing logo_url")

    def test_sports_category_filter(self):
        response = self.client.get(reverse('sports'), {'category': 'Traditional & Indigenous'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Silambam')
        self.assertContains(response, 'Kabaddi')
        self.assertContains(response, 'Kho Kho')


class ZoneAndSubZoneTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username="minister_admin", email="minister@tn.gov.in", password="password123")
        self.client.login(username="minister_admin", password="password123")
        from sports.models import Zone, District, DistrictPlace, DistrictSubZone
        self.zone = Zone.objects.create(
            name="North Zone",
            code="NORTH",
            headquarters="Chennai Complex",
            gold_medals_target=45,
            color="#2563eb",
            bg_gradient="from-blue-600 to-indigo-700"
        )
        self.district = District.objects.create(name="Chennai", slug="chennai", zone=self.zone)
        self.place1 = DistrictPlace.objects.create(district=self.district, name="Mylapore")
        self.place2 = DistrictPlace.objects.create(district=self.district, name="Anna Nagar")

    def test_update_zone_view_updates_hq_and_districts(self):
        url = reverse('update_zone', kwargs={'zone_id': self.zone.id})
        post_data = {
            'name': 'North Zone (Updated)',
            'headquarters': 'Grand Chennai Stadium Complex',
            'gold_medals_target': 50,
            'color': '#1d4ed8',
            'bg_gradient': 'from-blue-700 to-indigo-800',
            'description': 'Updated North Zone policy',
            'district_ids': [self.district.id]
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        
        self.zone.refresh_from_db()
        self.assertEqual(self.zone.name, 'North Zone (Updated)')
        self.assertEqual(self.zone.headquarters, 'Grand Chennai Stadium Complex')
        self.assertEqual(self.zone.gold_medals_target, 50)
        self.assertIn(self.district, self.zone.districts.all())

    def test_save_subzone_view_creates_subzone_and_assigns_places(self):
        url = reverse('save_subzone')
        post_data = {
            'district_id': self.district.id,
            'name': 'Chennai Central Sub-Zone',
            'contact_officer_name': 'R. Sundar',
            'contact_phone': '+91 98765 43210',
            'athletes_count': 150,
            'clubs_count': 20,
            'schools_count': 35,
            'is_active': 'on',
            'place_ids': [self.place1.id, self.place2.id],
            'new_place_name': 'Adyar'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        from sports.models import DistrictSubZone, DistrictPlace
        subzone = DistrictSubZone.objects.get(name='Chennai Central Sub-Zone', district=self.district)
        self.assertEqual(subzone.places.count(), 3)
        self.assertTrue(DistrictPlace.objects.filter(district=self.district, name='Adyar').exists())

    def test_delete_subzone_view(self):
        from sports.models import DistrictSubZone
        subzone = DistrictSubZone.objects.create(
            district=self.district,
            name='Temporary Sub-Zone'
        )
        url = reverse('delete_subzone', kwargs={'subzone_id': subzone.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DistrictSubZone.objects.filter(id=subzone.id).exists())


class RoleBasedAccessControlTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.athlete_user = User.objects.create_user(username="player_ramesh", password="password123")
        self.dso_user = User.objects.create_user(username="dso_madurai", password="password123")

    def test_unauthenticated_user_redirected_to_login(self):
        response = self.client.get(reverse('minister_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_athlete_blocked_from_minister_dashboard(self):
        self.client.login(username="player_ramesh", password="password123")
        response = self.client.get(reverse('minister_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('athlete_dashboard'))

    def test_athlete_blocked_from_collector_dashboard(self):
        self.client.login(username="player_ramesh", password="password123")
        response = self.client.get(reverse('collector_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('athlete_dashboard'))

    def test_dso_blocked_from_minister_dashboard(self):
        self.client.login(username="dso_madurai", password="password123")
        response = self.client.get(reverse('minister_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('collector_dashboard'))

    def test_logged_in_user_redirected_from_login_page(self):
        self.client.login(username="dso_madurai", password="password123")
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('collector_dashboard'))


class CoachDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.coach_user = User.objects.create_user(username="coach_gopichand", email="gopichand@tnsports.gov.in", password="password123")

    def test_coach_dashboard_authenticated_access(self):
        self.client.login(username="coach_gopichand", password="password123")
        response = self.client.get(reverse('coach_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_dashboard.html')
        self.assertContains(response, 'NIS Certified Coach')

    def test_coach_dashboard_add_trainee(self):
        self.client.login(username="coach_gopichand", password="password123")
        post_data = {
            'action_type': 'add_trainee',
            'trainee_name': 'S. Madesh Kumar',
            'trainee_sport': '100m Sprint',
            'trainee_emis': '3302010050101928'
        }
        response = self.client.post(reverse('coach_dashboard'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('coach_dashboard'))

    def test_portal_home_and_index_views(self):
        response_portal = self.client.get(reverse('portal_home'))
        self.assertEqual(response_portal.status_code, 200)
        self.assertTemplateUsed(response_portal, 'portal_landing.html')

        response_index = self.client.get(reverse('index'))
        self.assertEqual(response_index.status_code, 200)
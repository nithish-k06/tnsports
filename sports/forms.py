from django import forms
from .models import Club, Tournament, ContactMessage, Zone, DistrictSubZone, District, DistrictPlace



class LoginForm(forms.Form):
    email = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control-custom',
            'id': 'emailInput',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control-custom',
            'id': 'passwordInput',
            'autocomplete': 'current-password'
        })
    )

class ClubRegistrationForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            'name', 'registration_number', 'established_year', 
            'primary_sport', 'district', 'contact_person', 
            'email', 'phone', 'address', 'logo', 'reg_certificate'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Club or Academy Name'}),
            'registration_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'e.g. TN/SPO/2026/0123'}),
            'established_year': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'e.g. 2015'}),
            'primary_sport': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500'}),
            'district': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Secretary / President Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Official Email'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': '+91 98765 43210'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-sm focus:ring-emerald-500 focus:border-emerald-500', 'rows': 2, 'placeholder': 'Ground / Academy Address'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'w-full text-xs text-gray-500'}),
            'reg_certificate': forms.ClearableFileInput(attrs={'class': 'w-full text-xs text-gray-500'}),
        }


class TournamentSanctionRequestForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            'title', 'sport', 'district', 'level_category', 'age_condition',
            'organizer_name', 'organizer_contact', 'organizer_email', 'venue_name',
            'start_date', 'end_date', 'entry_deadline',
            'expected_teams', 'rulebook_doc'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'e.g., Kongu Trophy District Football 2026'}),
            'sport': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500'}),
            'district': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500'}),
            'level_category': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500'}),
            'age_condition': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'e.g. Under 14, Under 17, Under 25, Open 18+, Masters 35+'}),
            'organizer_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Club or Organizing Body'}),
            'organizer_contact': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': '+91 98765 43210'}),
            'organizer_email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'contact@organizer.com'}),
            'venue_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Stadium or Ground Name'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500'}),
            'entry_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500'}),
            'expected_teams': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': '16'}),
            'rulebook_doc': forms.ClearableFileInput(attrs={'class': 'w-full text-xs text-gray-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'level_category' in self.fields:
            self.fields['level_category'].required = False
            self.fields['level_category'].initial = 'GENERAL'
        if 'age_condition' in self.fields:
            self.fields['age_condition'].required = False
            self.fields['age_condition'].initial = 'Open Category (All Ages)'

    def clean_level_category(self):
        val = self.cleaned_data.get('level_category')
        return val or 'GENERAL'

    def clean_age_condition(self):
        val = self.cleaned_data.get('age_condition')
        return val or 'Open Category (All Ages)'


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500', 'placeholder': 'Enter your name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500', 'placeholder': 'Enter your email', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500', 'placeholder': 'Enter your phone'}),
            'message': forms.Textarea(attrs={'class': 'w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500', 'placeholder': 'Type your message...', 'rows': 4, 'required': True}),
        }


import datetime
from django.contrib.auth.models import User
from .models import Athlete, District, Sport, Coach

class AthleteRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'athlete@example.com',
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
            'id': 'emailInput'
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create strong password (min 6 chars)',
            'class': 'w-full px-4 py-3 pr-10 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
            'id': 'passwordInput'
        })
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'w-full px-4 py-3 pr-10 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
            'id': 'confirmPasswordInput'
        })
    )

    terms_confirmed = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must confirm that your details are true and accurate.'},
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500 transition cursor-pointer',
            'id': 'termsCheckbox'
        })
    )

    class Meta:
        model = Athlete
        fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'phone',
            'district',
            'primary_sport',
            'category',
            'skill_level',
            'club_or_school',
            'profile_photo',
            'id_proof',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Raman',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'firstNameInput'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Nathan',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'lastNameInput'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'dobInput'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none cursor-pointer',
                'id': 'genderSelect'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+91 98765 43210',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'phoneInput'
            }),
            'district': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none cursor-pointer',
                'id': 'districtSelect'
            }),
            'primary_sport': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none cursor-pointer',
                'id': 'primarySportSelect'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none cursor-pointer',
                'id': 'categorySelect'
            }),
            'skill_level': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none cursor-pointer',
                'id': 'skillLevelSelect'
            }),
            'club_or_school': forms.TextInput(attrs={
                'placeholder': 'e.g. St. Bede\'s HS / Loyola College / SDAT Academy',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'clubSchoolInput'
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'profilePhotoInput',
                'accept': 'image/*'
            }),
            'id_proof': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'idProofInput',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.all().order_by('name')
        self.fields['district'].empty_label = "Select District"
        self.fields['primary_sport'].queryset = Sport.objects.all().order_by('name')
        self.fields['primary_sport'].empty_label = "Select Primary Sport"

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists. Please login.")
        return email

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = datetime.date.today()
            age = (today - dob).days // 365
            if dob > today:
                raise forms.ValidationError("Date of birth cannot be in the future.")
            if age < 4:
                raise forms.ValidationError("Athlete must be at least 4 years old.")
        return dob

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match. Please enter matching passwords.")
            elif len(password) < 6:
                self.add_error('password', "Password must be at least 6 characters long.")
        return cleaned_data


class CoachRegistrationForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = [
            'name',
            'email',
            'phone',
            'sport',
            'district',
            'experience_years',
            'specialization',
            'photo',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. K. Ramanathan',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'coachNameInput',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'coach.email@tnsports.gov.in',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'coachEmailInput',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+91 98401 12345',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'coachPhoneInput',
                'required': True
            }),
            'sport': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none cursor-pointer',
                'id': 'coachSportSelect',
                'required': True
            }),
            'district': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none cursor-pointer',
                'id': 'coachDistrictSelect',
                'required': True
            }),
            'experience_years': forms.NumberInput(attrs={
                'placeholder': 'e.g. 10',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'coachExperienceInput',
                'min': 0,
                'required': True
            }),
            'specialization': forms.TextInput(attrs={
                'placeholder': 'e.g. Batting & Tactical Strategy / Sprint Training',
                'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-gray-900 text-sm transition-all duration-200 outline-none',
                'id': 'coachSpecializationInput',
                'required': True
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full text-xs text-gray-500 border border-gray-200 rounded-xl p-2.5 bg-gray-50 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer',
                'id': 'coachPhotoInput',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.all().order_by('name')
        self.fields['district'].empty_label = "Select District"
        self.fields['sport'].queryset = Sport.objects.all().order_by('name')
        self.fields['sport'].empty_label = "Select Sport Discipline"

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Coach.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A coach with this email address is already registered.")
        return email


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['name', 'code', 'headquarters', 'gold_medals_target', 'color', 'bg_gradient', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none', 'placeholder': 'e.g. North Zone'}),
            'code': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none', 'placeholder': 'NORTH'}),
            'headquarters': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none', 'placeholder': 'Stadium Complex HQ'}),
            'gold_medals_target': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none', 'placeholder': '45'}),
            'color': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none', 'placeholder': '#2563eb'}),
            'bg_gradient': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none', 'placeholder': 'from-blue-600 to-indigo-700'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none', 'rows': 3, 'placeholder': 'Zone summary...'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-emerald-500 outline-none'}),
        }


class DistrictSubZoneForm(forms.ModelForm):
    class Meta:
        model = DistrictSubZone
        fields = ['district', 'name', 'covered_places', 'contact_officer_name', 'contact_phone', 'athletes_count', 'clubs_count', 'schools_count', 'is_active']
        widgets = {
            'district': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'e.g. Madurai Urban Sub-Zone'}),
            'covered_places': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none', 'rows': 2, 'placeholder': 'e.g. RS Puram, Peelamedu, Gandhipuram'}),
            'contact_officer_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'Officer In-Charge Name'}),
            'contact_phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': '+91 98765 43210'}),
            'athletes_count': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': '250'}),
            'clubs_count': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': '12'}),
            'schools_count': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': '45'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded text-blue-600 focus:ring-blue-500 h-4 w-4'}),
        }
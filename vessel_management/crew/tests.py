# crew/tests.py
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta, date

from .models import Crew, CrewCertificate, Vessel, CrewAssignment, CertificateNotification
from .serializers import CrewSerializer, CrewCertificateSerializer

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class CrewModelTests(TestCase):
    """Test cases for Crew model methods"""
   
    def setUp(self):
        # Création d'un utilisateur de test
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Génération d'un token JWT pour l'utilisateur
        refresh = RefreshToken.for_user(self.user)
        
        # Ajouter le token dans les headers de toutes les requêtes client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.crew = Crew.objects.create(
            name="John Doe",
            rank="CAPTAIN",
            nationality="USA",
            date_of_birth=date(1980, 1, 1),
            passport_number="AB12345",
            seaman_book_number="SBN12345",
            phone_number="+12345678901",
            email="john.doe@example.com",
            address="123 Marine Drive, Seaport City",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+12345678902"
        )
        
        # Create certificates with different expiry dates
        today = timezone.now().date()
        
        # Expired certificate
        self.expired_cert = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="COC",
            certificate_name="Master Mariner",
            certificate_number="COC12345",
            issue_date=today - timedelta(days=400),
            expiry_date=today - timedelta(days=30),
            issuing_authority="Maritime Authority"
        )
        
        # Valid certificate
        self.valid_cert = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="STCW",
            certificate_name="Basic Safety Training",
            certificate_number="STCW12345",
            issue_date=today - timedelta(days=200),
            expiry_date=today + timedelta(days=165),
            issuing_authority="Maritime Safety Authority"
        )
        
        # Soon to expire certificate
        self.expiring_cert = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="MEDICAL",
            certificate_name="Medical Fitness",
            certificate_number="MED12345",
            issue_date=today - timedelta(days=335),
            expiry_date=today + timedelta(days=30),
            issuing_authority="Medical Center"
        )
    
    def test_get_active_certificates(self):
        """Test getting active certificates"""
        active_certs = self.crew.get_active_certificates()
        self.assertEqual(active_certs.count(), 2)
        self.assertIn(self.valid_cert, active_certs)
        self.assertIn(self.expiring_cert, active_certs)
        self.assertNotIn(self.expired_cert, active_certs)
    
    def test_get_expired_certificates(self):
        """Test getting expired certificates"""
        expired_certs = self.crew.get_expired_certificates()
        self.assertEqual(expired_certs.count(), 1)
        self.assertIn(self.expired_cert, expired_certs)
    
    def test_get_soon_to_expire_certificates(self):
        """Test getting certificates expiring soon"""
        soon_expiring = self.crew.get_soon_to_expire_certificates(days=60)
        self.assertEqual(soon_expiring.count(), 1)
        self.assertIn(self.expiring_cert, soon_expiring)


class CrewCertificateModelTests(TestCase):
    """Test cases for CrewCertificate model methods"""
    
    def setUp(self):
        self.crew = Crew.objects.create(
            name="John Doe",
            rank="CAPTAIN",
            nationality="USA",
            date_of_birth=date(1980, 1, 1),
            passport_number="AB12345",
            seaman_book_number="SBN12345",
            phone_number="+12345678901",
            email="john.doe@example.com",
            address="123 Marine Drive, Seaport City",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+12345678902"
        )
        
        today = timezone.now().date()
        
        # Expired certificate
        self.expired_cert = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="COC",
            certificate_name="Master Mariner",
            certificate_number="COC12345",
            issue_date=today - timedelta(days=400),
            expiry_date=today - timedelta(days=30),
            issuing_authority="Maritime Authority"
        )
        
        # Valid certificate
        self.valid_cert = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="STCW",
            certificate_name="Basic Safety Training",
            certificate_number="STCW12345",
            issue_date=today - timedelta(days=200),
            expiry_date=today + timedelta(days=165),
            issuing_authority="Maritime Safety Authority"
        )
    
    def test_is_expired(self):
        """Test certificate expiry check"""
        self.assertTrue(self.expired_cert.is_expired())
        self.assertFalse(self.valid_cert.is_expired())
    
    def test_days_until_expiry(self):
        """Test days until expiry calculation"""
        # For expired certificate, it should return negative days
        self.assertTrue(self.expired_cert.days_until_expiry() < 0)
        
        # For valid certificate, it should return positive days
        self.assertTrue(self.valid_cert.days_until_expiry() > 0)
        self.assertEqual(self.valid_cert.days_until_expiry(), 165)


class CrewAPITests(APITestCase):
    """Test cases for Crew API endpoints"""
    
    def setUp(self):
        # Create test crews
        self.crew1 = Crew.objects.create(
            name="John Doe",
            rank="CAPTAIN",
            nationality="USA",
            date_of_birth=date(1980, 1, 1),
            passport_number="AB12345",
            seaman_book_number="SBN12345",
            phone_number="+12345678901",
            email="john.doe@example.com",
            address="123 Marine Drive, Seaport City",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+12345678902"
        )
        
        self.crew2 = Crew.objects.create(
            name="Jane Smith",
            rank="CHIEF_OFFICER",
            nationality="UK",
            date_of_birth=date(1985, 5, 15),
            passport_number="CD67890",
            seaman_book_number="SBN67890",
            phone_number="+12345678903",
            email="jane.smith@example.com",
            address="456 Ocean Blvd, Maritime City",
            emergency_contact_name="John Smith",
            emergency_contact_phone="+12345678904"
        )
        
        # Create certificates
        today = timezone.now().date()
        
        self.cert1 = CrewCertificate.objects.create(
            crew=self.crew1,
            certificate_type="COC",
            certificate_name="Master Mariner",
            certificate_number="COC12345",
            issue_date=today - timedelta(days=400),
            expiry_date=today + timedelta(days=330),
            issuing_authority="Maritime Authority"
        )
        
        self.cert2 = CrewCertificate.objects.create(
            crew=self.crew2,
            certificate_type="COC",
            certificate_name="Chief Officer",
            certificate_number="COC67890",
            issue_date=today - timedelta(days=300),
            expiry_date=today - timedelta(days=30),  # Expired
            issuing_authority="Maritime Authority"
        )
    
    def test_get_crew_list(self):
        """Test getting list of crew members"""
        url = reverse('crew:crew-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_crew(self):
        """Test creating a new crew member"""
        url = reverse('crew:crew-list')
        data = {
            "name": "Robert Johnson",
            "rank": "SECOND_OFFICER",
            "nationality": "Canada",
            "date_of_birth": "1990-03-20",
            "passport_number": "EF13579",
            "seaman_book_number": "SBN13579",
            "phone_number": "+12345678905",
            "email": "robert.johnson@example.com",
            "address": "789 Sailor Ave, Harbor City",
            "emergency_contact_name": "Mary Johnson",
            "emergency_contact_phone": "+12345678906",
            "is_active": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Crew.objects.count(), 3)
    
    def test_get_crew_detail(self):
        """Test getting detailed information about a crew member"""
        url = reverse('crew:crew-detail', args=[self.crew1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.crew1.name)
    
    def test_filter_crew_by_rank(self):
        """Test filtering crew by rank"""
        url = reverse('crew:crew-by-rank') + f'?rank=CAPTAIN'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.crew1.name)
    
    def test_filter_crew_with_expired_certificates(self):
        """Test filtering crew with expired certificates"""
        url = reverse('crew:crew-with-expired-certificates')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.crew2.name)


class CrewCertificateAPITests(APITestCase):
    """Test cases for CrewCertificate API endpoints"""
    
    def setUp(self):
        # Create test crew
        self.crew = Crew.objects.create(
            name="John Doe",
            rank="CAPTAIN",
            nationality="USA",
            date_of_birth=date(1980, 1, 1),
            passport_number="AB12345",
            seaman_book_number="SBN12345",
            phone_number="+12345678901",
            email="john.doe@example.com",
            address="123 Marine Drive, Seaport City",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+12345678902"
        )
        
        # Create certificates
        today = timezone.now().date()
        
        self.cert1 = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="COC",
            certificate_name="Master Mariner",
            certificate_number="COC12345",
            issue_date=today - timedelta(days=400),
            expiry_date=today + timedelta(days=330),
            issuing_authority="Maritime Authority"
        )
        
        self.cert2 = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="MEDICAL",
            certificate_name="Medical Fitness",
            certificate_number="MED12345",
            issue_date=today - timedelta(days=335),
            expiry_date=today - timedelta(days=30),  # Expired
            issuing_authority="Medical Center"
        )
    
    def test_get_certificate_list(self):
        """Test getting list of certificates"""
        url = reverse('crew:crewcertificate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_certificate(self):
        """Test creating a new certificate"""
        url = reverse('crew:crewcertificate-list')
        today = timezone.now().date()
        data = {
            "crew": self.crew.id,
            "certificate_type": "STCW",
            "certificate_name": "Basic Safety Training",
            "certificate_number": "STCW12345",
            "issue_date": str(today - timedelta(days=200)),
            "expiry_date": str(today + timedelta(days=165)),
            "issuing_authority": "Maritime Safety Authority"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CrewCertificate.objects.count(), 3)
    
    def test_get_expired_certificates(self):
        """Test getting expired certificates"""
        url = reverse('crew:crewcertificate-expired')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['certificate_name'], self.cert2.certificate_name)
    
    def test_get_certificates_by_crew(self):
        """Test getting certificates for a specific crew member"""
        url = reverse('crew:crewcertificate-by-crew') + f'?crew_id={self.crew.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class NotificationGenerationTests(APITestCase):
    """Test cases for certificate notification generation"""
    
    def setUp(self):
        # Create test crew
        self.crew = Crew.objects.create(
            name="John Doe",
            rank="CAPTAIN",
            nationality="USA",
            date_of_birth=date(1980, 1, 1),
            passport_number="AB12345",
            seaman_book_number="SBN12345",
            phone_number="+12345678901",
            email="john.doe@example.com",
            address="123 Marine Drive, Seaport City",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+12345678902"
        )
        
        # Create certificates with strategic expiry dates
        today = timezone.now().date()
        
        # Certificate expiring in exactly 30 days
        self.cert_30_days = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="MEDICAL",
            certificate_name="Medical Fitness",
            certificate_number="MED12345",
            issue_date=today - timedelta(days=335),
            expiry_date=today + timedelta(days=30),
            issuing_authority="Medical Center"
        )
        
        # Certificate expiring in exactly 60 days
        self.cert_60_days = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="STCW",
            certificate_name="Basic Safety Training",
            certificate_number="STCW12345",
            issue_date=today - timedelta(days=305),
            expiry_date=today + timedelta(days=60),
            issuing_authority="Maritime Safety Authority"
        )
        
        # Certificate expiring in exactly 90 days
        self.cert_90_days = CrewCertificate.objects.create(
            crew=self.crew,
            certificate_type="COC",
            certificate_name="Master Mariner",
            certificate_number="COC12345",
            issue_date=today - timedelta(days=275),
            expiry_date=today + timedelta(days=90),
            issuing_authority="Maritime Authority"
        )
    
    def test_generate_notifications(self):
        """Test generating notifications for certificates expiring soon"""
        url = reverse('crew:crewcertificate-generate-notifications')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should create 3 notifications (one for each certificate at their threshold)
        self.assertEqual(CertificateNotification.objects.count(), 3)
        
        # Check notification details
        notif_30 = CertificateNotification.objects.get(certificate=self.cert_30_days)
        self.assertEqual(notif_30.days_before_expiry, 30)
        self.assertEqual(notif_30.status, 'PENDING')
        
        notif_60 = CertificateNotification.objects.get(certificate=self.cert_60_days)
        self.assertEqual(notif_60.days_before_expiry, 60)
        
        notif_90 = CertificateNotification.objects.get(certificate=self.cert_90_days)
        self.assertEqual(notif_90.days_before_expiry, 90)
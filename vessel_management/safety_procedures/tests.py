from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import (
    ProcedureCategory, Procedure, ProcedureReview, 
    ProcedureAcknowledgment, ProcedureVersion
)
from .utils import generate_next_version


User = get_user_model()


class ProcedureModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = ProcedureCategory.objects.create(
            name='Safety',
            code='SAF',
            description='Safety procedures'
        )
        self.procedure = Procedure.objects.create(
            title='Fire Safety',
            document_type='PROCEDURE',
            category=self.category,
            content='Test content',
            version='1.0',
            created_by=self.user,
            review_interval_months=6
        )
    
    def test_procedure_creation(self):
        self.assertEqual(self.procedure.title, 'Fire Safety')
        self.assertEqual(self.procedure.version, '1.0')
        self.assertEqual(self.procedure.review_status, 'DRAFT')
    
    def test_procedure_versioning(self):
        new_procedure = self.procedure.create_new_version('1.1', self.user)
        self.assertEqual(new_procedure.version, '1.1')
        self.assertEqual(new_procedure.review_status, 'CURRENT')
        
        # Check that version history was created
        self.assertEqual(ProcedureVersion.objects.count(), 1)
        version = ProcedureVersion.objects.first()
        self.assertEqual(version.version, '1.1')
        self.assertEqual(version.procedure, new_procedure)
    
    def test_review_date_calculation(self):
        now = timezone.now()
        self.procedure.last_reviewed_date = now
        self.procedure.save()
        
        self.assertIsNotNone(self.procedure.next_review_date)
        # Should be 6 months from now (with small time difference due to processing)
        diff = self.procedure.next_review_date - now
        self.assertTrue(170 <= diff.days <= 190)  # Approximately 6 months
    
    def test_review_status_update(self):
        # Set the procedure to be reviewed today
        now = timezone.now()
        self.procedure.last_reviewed_date = now
        self.procedure.save()
        
        # Current status
        self.assertEqual(self.procedure.review_status, 'CURRENT')
        
        # Set review date to be coming up soon
        self.procedure.next_review_date = now + timezone.timedelta(days=20)
        self.procedure.save()
        self.assertEqual(self.procedure.review_status, 'DUE_SOON')
        
        # Set review date to be in the past
        self.procedure.next_review_date = now - timezone.timedelta(days=10)
        self.procedure.save()
        self.assertEqual(self.procedure.review_status, 'OVERDUE')


class ProcedureAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = ProcedureCategory.objects.create(
            name='Safety',
            code='SAF',
            description='Safety procedures'
        )
        self.procedure = Procedure.objects.create(
            title='Fire Safety',
            document_type='PROCEDURE',
            category=self.category,
            content='Test content',
            version='1.0',
            created_by=self.user,
            review_interval_months=6
        )
    
    def test_list_procedures(self):
        url = '/api/safety/procedures/'  # Assuming this is your API endpoint
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_procedure(self):
        url = '/api/safety/procedures/'
        data = {
            'title': 'Emergency Response',
            'document_type': 'MANUAL',
            'category': self.category.id,
            'content': 'Emergency response details',
            'version': '1.0',
            'review_interval_months': 12
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Procedure.objects.count(), 2)
    
    def test_create_version(self):
        url = f'/api/safety/procedures/{self.procedure.id}/create_version/'
        data = {
            'change_notes': 'Updated fire safety content'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['version'], '1.1')  # Assuming next version is 1.1
    
    def test_review_procedure(self):
        url = f'/api/safety/procedures/{self.procedure.id}/review/'
        data = {
            'comments': 'Looks good',
            'changes_required': False,
            'approved': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that procedure was updated
        self.procedure.refresh_from_db()
        self.assertEqual(self.procedure.review_status, 'CURRENT')
        self.assertEqual(ProcedureReview.objects.count(), 1)
    
    def test_acknowledge_procedure(self):
        url = f'/api/safety/procedures/{self.procedure.id}/acknowledge/'
        data = {
            'comments': 'I have read and understood this procedure'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProcedureAcknowledgment.objects.count(), 1)
        
        # Test acknowledging same version twice
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProcedureAcknowledgment.objects.count(), 1)  # Still only one
    
    def test_search_procedures(self):
        # Create another procedure for testing search
        Procedure.objects.create(
            title='Man Overboard Procedure',
            document_type='PROCEDURE',
            category=self.category,
            content='Steps to take in case of man overboard',
            version='1.0',
            created_by=self.user,
            tags='emergency, overboard, rescue'
        )
        
        url = '/api/safety/procedures/search/?q=overboard'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Man Overboard Procedure')
        
        # Test category filter
        url = f'/api/safety/procedures/search/?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Both procedures
    
    def test_review_due_procedures(self):
        # Set one procedure to be due for review
        self.procedure.last_reviewed_date = timezone.now() - timezone.timedelta(days=150)
        self.procedure.next_review_date = timezone.now() - timezone.timedelta(days=30)
        self.procedure.save()
        
        url = '/api/safety/procedures/review_due/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.procedure.id)


class UtilsTests(TestCase):
    def test_generate_next_version(self):
        # Test semantic versioning
        self.assertEqual(generate_next_version('1.0.0'), '1.0.1')
        self.assertEqual(generate_next_version('2.3.5'), '2.3.6')
        
        # Test major.minor versioning
        self.assertEqual(generate_next_version('1.0'), '1.1')
        self.assertEqual(generate_next_version('2.9'), '2.10')
        
        # Test numeric versioning
        self.assertEqual(generate_next_version('1'), '2')
        self.assertEqual(generate_next_version('42'), '43')
        
        # Test custom versioning
        self.assertEqual(generate_next_version('2023A'), '2023A.1')
        self.assertEqual(generate_next_version('REV-B'), 'REV-B.1')


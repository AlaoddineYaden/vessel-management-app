# audit_inspection/management/commands/generate_notifications.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

from audit_inspection.models import (
    Audit, AuditFinding, AuditNotification
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate notifications for upcoming and overdue audits and findings'
    
    def handle(self, *args, **options):
        self.generate_audit_notifications()
        self.generate_finding_notifications()
        self.stdout.write(self.style.SUCCESS('Successfully generated notifications'))
    
    def generate_audit_notifications(self):
        today = timezone.now().date()
        
        # Delete old notifications that haven't been sent
        AuditNotification.objects.filter(
            audit__isnull=False,
            is_sent=False,
            finding__isnull=True
        ).delete()
        
        # Upcoming audits (due in 30 days)
        upcoming_audits = Audit.objects.filter(
            status='PLANNED',
            planned_date__gt=today,
            planned_date__lte=today + timezone.timedelta(days=30)
        )
        
        # Create notifications for upcoming audits
        for audit in upcoming_audits:
            days_until_due = (audit.planned_date - today).days
            
            # Create notification
            notification = AuditNotification(
                audit=audit,
                notification_type='DUE_SOON',
                message=f"Audit #{audit.id} ({audit.audit_type}) is due in {days_until_due} days on {audit.planned_date}."
            )
            notification.save()
            
            # Add recipients - auditor, vessel manager, etc.
            notification.recipients.add(audit.auditor)
            notification.recipients.add(audit.created_by)
            # Add vessel managers (in a real app, this would link to vessel management)
            # for manager in audit.vessel.managers.all():
            #     notification.recipients.add(manager)
        
        # Overdue audits
        overdue_audits = Audit.objects.filter(
            Q(status='PLANNED', planned_date__lt=today) |
            Q(status='OVERDUE')
        )
        
        # Create notifications for overdue audits
        for audit in overdue_audits:
            days_overdue = (today - audit.planned_date).days
            
            # Create notification
            notification = AuditNotification(
                audit=audit,
                notification_type='OVERDUE',
                message=f"Audit #{audit.id} ({audit.audit_type}) is overdue by {days_overdue} days. It was due on {audit.planned_date}."
            )
            notification.save()
            
            # Add recipients - auditor, vessel manager, etc.
            notification.recipients.add(audit.auditor)
            notification.recipients.add(audit.created_by)
            # Add vessel managers (in a real app, this would link to vessel management)
            # for manager in audit.vessel.managers.all():
            #     notification.recipients.add(manager)
            
            # Also add managers/supervisors
            managers = User.objects.filter(is_staff=True)
            for manager in managers:
                notification.recipients.add(manager)
    
    def generate_finding_notifications(self):
        today = timezone.now().date()
        
        # Delete old notifications that haven't been sent
        AuditNotification.objects.filter(
            finding__isnull=False,
            is_sent=False
        ).delete()
        
        # Upcoming findings due (due in 14 days)
        upcoming_findings = AuditFinding.objects.filter(
            status__in=['OPEN', 'IN_PROGRESS'],
            due_date__gt=today,
            due_date__lte=today + timezone.timedelta(days=14)
        )
        
        # Create notifications for upcoming findings
        for finding in upcoming_findings:
            days_until_due = (finding.due_date - today).days
            
            # Create notification
            notification = AuditNotification(
                finding=finding,
                notification_type='FINDING_DUE',
                message=f"Finding #{finding.id} from Audit #{finding.audit.id} is due in {days_until_due} days on {finding.due_date}."
            )
            notification.save()
            
            # Add recipients - assigned person, auditor, etc.
            if finding.assigned_to:
                notification.recipients.add(finding.assigned_to)
            notification.recipients.add(finding.audit.auditor)
        
        # Overdue findings
        overdue_findings = AuditFinding.objects.filter(
            status__in=['OPEN', 'IN_PROGRESS'],
            due_date__lt=today
        )
        
        # Create notifications for overdue findings
        for finding in overdue_findings:
            days_overdue = (today - finding.due_date).days
            
            # Create notification
            notification = AuditNotification(
                finding=finding,
                notification_type='FINDING_OVERDUE',
                message=f"Finding #{finding.id} from Audit #{finding.audit.id} is overdue by {days_overdue} days. It was due on {finding.due_date}."
            )
            notification.save()
            
            # Add recipients - assigned person, auditor, managers
            if finding.assigned_to:
                notification.recipients.add(finding.assigned_to)
            notification.recipients.add(finding.audit.auditor)
            
            # Also add managers/supervisors
            managers = User.objects.filter(is_staff=True)
            for manager in managers:
                notification.recipients.add(manager)

from django.utils import timezone
from django.db.models import Count, Q
from .models import NonConformity, CorrectiveAction, PreventiveAction

def generate_trend_analysis(vessel_id, from_date=None, to_date=None):
    """
    Generate trend analysis for non-conformities for a specific vessel
    """
    queryset = NonConformity.objects.filter(vessel_id=vessel_id)
    
    if from_date:
        queryset = queryset.filter(detection_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(detection_date__lte=to_date)
    
    # Analysis by severity
    severity_trends = queryset.values('severity').annotate(count=Count('id'))
    
    # Analysis by source type
    source_trends = queryset.values('source_type').annotate(count=Count('id'))
    
    # Analysis by status
    status_trends = queryset.values('status').annotate(count=Count('id'))
    
    # Analysis of corrective actions
    total_corrective_actions = CorrectiveAction.objects.filter(
        non_conformity__in=queryset
    ).count()
    
    completed_corrective_actions = CorrectiveAction.objects.filter(
        non_conformity__in=queryset,
        completed_date__isnull=False
    ).count()
    
    overdue_corrective_actions = CorrectiveAction.objects.filter(
        non_conformity__in=queryset,
        completed_date__isnull=True,
        due_date__lt=timezone.now().date()
    ).count()
    
    return {
        'vessel_id': vessel_id,
        'total_nonconformities': queryset.count(),
        'severity_distribution': list(severity_trends),
        'source_distribution': list(source_trends),
        'status_distribution': list(status_trends),
        'corrective_actions': {
            'total': total_corrective_actions,
            'completed': completed_corrective_actions,
            'overdue': overdue_corrective_actions,
            'completion_rate': (completed_corrective_actions / total_corrective_actions * 100) if total_corrective_actions > 0 else 0
        }
    }

def get_overdue_actions():
    """
    Get all overdue corrective and preventive actions.
    """
    today = timezone.now().date()
    
    overdue_corrective_actions = CorrectiveAction.objects.filter(
        Q(due_date__lt=today) & Q(completed_date__isnull=True)
    )
    
    overdue_preventive_actions = PreventiveAction.objects.filter(
        Q(due_date__lt=today) & Q(completed_date__isnull=True)
    )
    
    return {
        'corrective_actions': overdue_corrective_actions,
        'preventive_actions': overdue_preventive_actions
    }

def get_vessel_nonconformities(vessel_id, status=None):
    """
    Get all non-conformities for a specific vessel.
    Optionally filter by status.
    """
    query = Q(vessel_id=vessel_id)
    if status:
        query &= Q(status=status)
    
    return NonConformity.objects.filter(query)

def get_user_assignments(user_id, include_completed=False):
    """
    Get all corrective and preventive actions assigned to a user.
    Optionally include completed actions.
    """
    query = Q(assigned_to_id=user_id)
    if not include_completed:
        query &= Q(completed_date__isnull=True)
    
    corrective_actions = CorrectiveAction.objects.filter(query)
    preventive_actions = PreventiveAction.objects.filter(query)
    
    return {
        'corrective_actions': corrective_actions,
        'preventive_actions': preventive_actions
    }

def close_nonconformity(nonconformity_id, user):
    """
    Close a non-conformity and update related actions.
    """
    try:
        nonconformity = NonConformity.objects.get(id=nonconformity_id)
        nonconformity.status = 'CLOSED'
        nonconformity.save()
        
        # Update all related corrective and preventive actions
        CorrectiveAction.objects.filter(non_conformity=nonconformity).update(
            completed_date=timezone.now().date()
        )
        
        PreventiveAction.objects.filter(non_conformity=nonconformity).update(
            completed_date=timezone.now().date(),
            status='COMPLETED'
        )
        
        return True
    except NonConformity.DoesNotExist:
        return False

def verify_corrective_action(action_id, user, verified=True, comments=None):
    """
    Verify or reject a corrective action.
    """
    try:
        action = CorrectiveAction.objects.get(id=action_id)
        action.verification_status = 'VERIFIED' if verified else 'REJECTED'
        if comments:
            action.verification_comments = comments
        action.save()
        return True
    except CorrectiveAction.DoesNotExist:
        return False

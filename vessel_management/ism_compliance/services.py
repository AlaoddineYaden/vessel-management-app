from django.utils import timezone
from datetime import timedelta
from .models import ComplianceItem, ComplianceReview


class ComplianceService:
    """Service class containing business logic for compliance management"""
    
    @staticmethod
    def calculate_risk_level(compliance_item):
        """Calculate risk level based on compliance status and ISM section"""
        # High-risk sections of ISM code
        high_risk_sections = ['5', '6', '7', '8', '10']
        
        if compliance_item.compliance_status == 'non_compliant':
            if compliance_item.ism_requirement.ism_section in high_risk_sections:
                return 'high'
            return 'medium'
        elif compliance_item.compliance_status == 'partially_compliant':
            if compliance_item.ism_requirement.ism_section in high_risk_sections:
                return 'medium'
            return 'low'
        elif compliance_item.compliance_status == 'compliant':
            return 'low'
        
        return 'medium'  # Default for pending or not applicable
    
    @staticmethod
    def schedule_next_review(compliance_item):
        """Schedule next review date based on risk level"""
        risk_review_intervals = {
            'high': timedelta(days=30),    # Monthly for high risk
            'medium': timedelta(days=90),  # Quarterly for medium risk
            'low': timedelta(days=180),    # Semi-annually for low risk
        }
        
        interval = risk_review_intervals.get(compliance_item.risk_level, timedelta(days=90))
        return timezone.now() + interval
    
    @staticmethod
    def calculate_compliance_metrics(vessel_id):
        """Calculate compliance metrics for a vessel"""
        items = ComplianceItem.objects.filter(vessel_id=vessel_id)
        total_items = items.count()
        
        if total_items == 0:
            return {
                'vessel_id': vessel_id,
                'compliance_rate': 0,
                'non_compliance_rate': 0,
                'high_risk_items': 0,
                'pending_reviews': 0,
            }
        
        compliant_items = items.filter(compliance_status='compliant').count()
        non_compliant_items = items.filter(compliance_status='non_compliant').count()
        partial_items = items.filter(compliance_status='partially_compliant').count()
        high_risk_items = items.filter(risk_level='high').count()
        pending_reviews = ComplianceReview.objects.filter(
            compliance_item__vessel_id=vessel_id, 
            status='scheduled',
            scheduled_date__lte=timezone.now()
        ).count()
        
        # Calculate weighted compliance rate (compliant = 1, partial = 0.5, others = 0)
        compliance_rate = (compliant_items + (partial_items * 0.5)) / total_items * 100
        non_compliance_rate = non_compliant_items / total_items * 100
        
        return {
            'vessel_id': vessel_id,
            'total_items': total_items,
            'compliant_items': compliant_items,
            'non_compliant_items': non_compliant_items,
            'partial_items': partial_items,
            'compliance_rate': round(compliance_rate, 2),
            'non_compliance_rate': round(non_compliance_rate, 2),
            'high_risk_items': high_risk_items,
            'pending_reviews': pending_reviews,
        }
    
    @staticmethod
    def generate_gap_analysis(vessel_id):
        """Generate gap analysis for a vessel"""
        items = ComplianceItem.objects.filter(
            vessel_id=vessel_id,
            compliance_status__in=['non_compliant', 'partially_compliant']
        ).select_related('ism_requirement')
        
        gaps = []
        for item in items:
            gaps.append({
                'item_id': item.id,
                'requirement_code': item.ism_requirement.requirement_code,
                'requirement_text': item.ism_requirement.requirement_text,
                'compliance_status': item.compliance_status,
                'risk_level': item.risk_level,
                'assessment_date': item.assessment_date,
                'comments': item.comments,
            })
            
        return {
            'vessel_id': vessel_id,
            'analysis_date': timezone.now(),
            'gaps': gaps,
            'total_gaps': len(gaps),
        }

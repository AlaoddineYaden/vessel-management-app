from django.db.models import Sum, Avg, Count, Min, Max
from django.db import connection
from datetime import datetime, timedelta

class DataAggregator:
    """Base class for data aggregation operations"""
    
    @staticmethod
    def execute_raw_query(query, params=None):
        """Execute raw SQL query for complex aggregations"""
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def get_time_series_data(model, date_field, value_field, period_start, period_end, interval='day'):
        """Generate time series data for trend analysis"""
        if interval == 'day':
            date_trunc = 'date_trunc(\'day\', "{}")'.format(date_field)
        elif interval == 'week':
            date_trunc = 'date_trunc(\'week\', "{}")'.format(date_field)
        elif interval == 'month':
            date_trunc = 'date_trunc(\'month\', "{}")'.format(date_field)
        else:
            raise ValueError(f"Unsupported interval: {interval}")
        
        query = f"""
            SELECT 
                {date_trunc} as period,
                SUM("{value_field}") as total,
                COUNT(*) as count,
                AVG("{value_field}") as average
            FROM "{model._meta.db_table}"
            WHERE "{date_field}" BETWEEN %s AND %s
            GROUP BY period
            ORDER BY period
        """
        
        return DataAggregator.execute_raw_query(query, [period_start, period_end])


class ComplianceAggregator(DataAggregator):
    """Aggregates data for compliance reports"""
    
    @staticmethod
    def get_compliance_by_vessel(start_date=None, end_date=None, vessel_ids=None):
        """Get compliance metrics aggregated by vessel"""
        # This would be implemented with actual models from the vessel application
        # For now, we return a mock implementation
        return {
            'method': 'get_compliance_by_vessel',
            'params': {
                'start_date': start_date,
                'end_date': end_date,
                'vessel_ids': vessel_ids
            }
        }


class MaintenanceAggregator(DataAggregator):
    """Aggregates data for maintenance reports"""
    
    @staticmethod
    def get_maintenance_status_summary(start_date=None, end_date=None, vessel_ids=None):
        """Get maintenance status metrics aggregated by vessel"""
        # This would be implemented with actual models from the vessel application
        # For now, we return a mock implementation
        return {
            'method': 'get_maintenance_status_summary',
            'params': {
                'start_date': start_date,
                'end_date': end_date,
                'vessel_ids': vessel_ids
            }
        }


class CertificationAggregator(DataAggregator):
    """Aggregates data for certification reports"""
    
    @staticmethod
    def get_certification_expiry_summary(days_to_expiry=90):
        """Get certification expiry summary for vessels"""
        # This would be implemented with actual models from the vessel application
        # For now, we return a mock implementation
        return {
            'method': 'get_certification_expiry_summary',
            'params': {
                'days_to_expiry': days_to_expiry
            }
        } 
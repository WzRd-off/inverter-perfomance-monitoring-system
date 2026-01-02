from datetime import datetime

class Calculator:
    @staticmethod
    def calculate_efficiency(ac_power, dc_power):
        """
        Формула (1): n = (Pac / Pdc) * 100%
        """
        if not dc_power or dc_power == 0:
            return 0.0
        return (ac_power / dc_power) * 100.0

    @staticmethod
    def calculate_generation(power_records):
        """
        Формула (2): E = Sum((Pi + Pi+1)/2 * dt)
        """
        total_energy = 0.0
        if len(power_records) < 2:
            return 0.0

        for i in range(len(power_records) - 1):
            p1 = power_records[i]['ac_output_power'] or 0
            p2 = power_records[i+1]['ac_output_power'] or 0
            
            t1_str = power_records[i]['timestamp']
            t2_str = power_records[i+1]['timestamp']
            
            try:
                t1 = Calculator._parse_date(t1_str)
                t2 = Calculator._parse_date(t2_str)
                
                if not t1 or not t2:
                    continue
                
                dt_seconds = (t2 - t1).total_seconds()
                energy_joules = ((p1 + p2) / 2) * dt_seconds
                total_energy += energy_joules / 3600.0
            except Exception:
                continue

        return total_energy

    @staticmethod
    def calculate_reliability_index(error_count, total_period_hours):
        """
        R = 1 - (Час помилок / Загальний час)
        """
        if total_period_hours <= 0:
            return 1.0
            
        assumed_downtime_hours = error_count * 0.25 
        
        ratio = assumed_downtime_hours / total_period_hours
        reliability = 1.0 - ratio
        
        return max(0.0, reliability)

    @staticmethod
    def _parse_date(date_str):
        """
        Гнучкий парсинг дати.
        Підтримує і стандарт з 'T', і з пробілом.
        """
        if not date_str:
            return None
            
        formats = [
            "%Y-%m-%dT%H:%M:%S",       # ISO format (з T)
            "%Y-%m-%d %H:%M:%S",       # SQL Standard (пробіл)
            "%Y-%m-%dT%H:%M:%S.%f",    # ISO з мікросекундами
            "%Y-%m-%d %H:%M:%S.%f"     # SQL з мікросекундами
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
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
        Результат у кВт*год (kWh) або Вт*год (Wh) залежно від вхідних даних.
        Тут вважаємо, що вхід у Вт, результат повертаємо у Вт*год.
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
                
                # Якщо різниця в часі занадто велика (наприклад, > 1 години), 
                # це означає розрив у даних, пропускаємо інтервал
                if dt_seconds > 3600:
                    continue

                # Формула трапецій: (P1 + P2) / 2 * dt
                # Потужність у Вт, час у секундах -> Енергія у Джоулях
                energy_joules = ((p1 + p2) / 2) * dt_seconds
                
                # Переводимо Джоулі у Вт*год (1 Вт*год = 3600 Дж)
                total_energy += energy_joules / 3600.0
            except Exception:
                continue

        return total_energy

    @staticmethod
    def calculate_reliability_index(error_count, total_period_hours):
        """
        Формула (3): R = 1 - (N_critical / T_warranty)
        В контексті статистики за період: 1 - (Час помилок / Загальний час)
        """
        if total_period_hours <= 0:
            return 1.0
            
        # Припускаємо, що кожна помилка - це простий 15 хвилин (0.25 години), 
        # якщо немає точних даних про тривалість
        assumed_downtime_hours = error_count * 0.25 
        
        ratio = assumed_downtime_hours / total_period_hours
        reliability = 1.0 - ratio
        
        return max(0.0, reliability)

    @staticmethod
    def calculate_violation_intensity(violation_count, total_time_hours):
        """
        Формула (4): F = N_violations / T
        Інтенсивність порушень (порушень на годину).
        """
        if total_time_hours <= 0:
            return 0.0
        
        return violation_count / total_time_hours

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
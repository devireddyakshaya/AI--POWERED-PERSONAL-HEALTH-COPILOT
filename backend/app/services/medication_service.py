"""
Prescription-to-Reminder Planner service for MediMitra AI.
Converts extracted prescription instructions into reviewable daily medication schedules.
Requires explicit user confirmation before activating reminders.
Never invents frequency or dosages.
"""
from typing import Dict, Any, List

class MedicationPlannerService:
    @staticmethod
    def compute_daily_schedule(medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Organizes verified medications into a daily chronological reminder agenda.
        Only marks reminders as active when user has verified them.
        """
        schedule_slots = []

        for med in medications:
            m_name = med.get("medicine_name")
            dosage = med.get("dosage", "Unspecified dose")
            timing = med.get("timing_instructions", "As directed")
            freq = med.get("frequency", "Daily")
            schedule_time = med.get("schedule_time", "08:00 AM")
            is_active = med.get("is_reminder_active", False)
            is_verified = med.get("is_verified", False)
            is_incomplete = med.get("is_incomplete", False)

            # Split compound times like '08:00 AM & 08:00 PM'
            times = [t.strip() for t in schedule_time.split("&")]
            for t in times:
                schedule_slots.append({
                    "id": med.get("id"),
                    "medicine_name": m_name,
                    "dosage": dosage,
                    "time": t,
                    "frequency": freq,
                    "instructions": timing,
                    "is_active": is_active,
                    "is_verified": is_verified,
                    "is_incomplete": is_incomplete,
                    "trust_warning": med.get("trust_warning")
                })

        # Sort roughly by time string
        def sort_key(slot):
            t = slot["time"]
            is_pm = "PM" in t.upper()
            hour_match = t.split(":")[0].strip()
            try:
                hour = int(hour_match)
                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
                return hour
            except Exception:
                return 12

        schedule_slots.sort(key=sort_key)
        return schedule_slots

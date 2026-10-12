"""
Health Change Detector service for MediMitra AI.
Compares two reports from the same patient with strict clinical safety:
- Matches tests only when test identity and units are compatible.
- Evaluates whether values moved closer to or farther from reference ranges.
- Flags incompatible units or methods as unsafe comparisons.
- Never claims numerical improvement proves clinical recovery.
"""
from typing import Dict, Any, List, Optional
from backend.app.schemas import ComparisonItem, ReportComparisonResponse

class HealthChangeDetectorService:
    @staticmethod
    def compare_reports(
        report_a: Dict[str, Any],
        report_b: Dict[str, Any]
    ) -> ReportComparisonResponse:
        """
        Compares Report A (older) and Report B (newer).
        Ensures strict unit compatibility and clinical safety flags.
        """
        obs_a_list = report_a.get("observations", [])
        obs_b_list = report_b.get("observations", [])

        # Index tests from Report A by canonical test name
        map_a = {HealthChangeDetectorService._normalize_name(o["test_name"]): o for o in obs_a_list}
        map_b = {HealthChangeDetectorService._normalize_name(o["test_name"]): o for o in obs_b_list}

        matched_items: List[ComparisonItem] = []
        unmatched_a: List[str] = []
        unmatched_b: List[str] = []

        all_safe = True

        for norm_name, obs_a in map_a.items():
            if norm_name in map_b:
                obs_b = map_b[norm_name]
                comparison_item = HealthChangeDetectorService._compare_single_test(obs_a, obs_b)
                if not comparison_item.is_safe_comparison:
                    all_safe = False
                matched_items.append(comparison_item)
            else:
                unmatched_a.append(obs_a.get("test_name", norm_name))

        for norm_name, obs_b in map_b.items():
            if norm_name not in map_a:
                unmatched_b.append(obs_b.get("test_name", norm_name))

        disclaimer = (
            "Medical Safety Notice: MediMitra AI provides numerical comparisons for informational tracking only. "
            "A numerical shift toward normal limits does not independently confirm clinical recovery or remission. "
            "Always review these findings with your attending physician."
        )

        warning_notes = None
        if not all_safe:
            warning_notes = "One or more matched tests had unit or methodology mismatches and were flagged for user safety."

        return ReportComparisonResponse(
            report_a_id=report_a["id"],
            report_b_id=report_b["id"],
            report_a_date=report_a.get("document_date", "Prior Date"),
            report_b_date=report_b.get("document_date", "Recent Date"),
            safe_comparison=all_safe,
            warning_notes=warning_notes,
            matched_tests=matched_items,
            unmatched_tests_a=unmatched_a,
            unmatched_tests_b=unmatched_b,
            disclaimer=disclaimer
        )

    @staticmethod
    def _normalize_name(test_name: str) -> str:
        """Normalizes test name for robust pairing."""
        clean = test_name.lower().strip()
        if "fasting" in clean and ("glucose" in clean or "sugar" in clean):
            return "fasting_glucose"
        if "hba1c" in clean or "glycated" in clean:
            return "hba1c"
        if "cholesterol" in clean and "total" in clean:
            return "total_cholesterol"
        if "triglyceride" in clean:
            return "triglycerides"
        if "creatinine" in clean:
            return "serum_creatinine"
        if "hdl" in clean:
            return "hdl"
        if "ldl" in clean:
            return "ldl"
        if "tsh" in clean:
            return "tsh"
        if "hemoglobin" in clean or "hb" in clean:
            return "hemoglobin"
        return clean

    @staticmethod
    def _compare_single_test(obs_a: Dict[str, Any], obs_b: Dict[str, Any]) -> ComparisonItem:
        """
        Compares two observation records of the same test.
        Validates units and evaluates range shift direction.
        """
        test_name = obs_b.get("test_name") or obs_a.get("test_name")
        unit_a = (obs_a.get("unit") or "").strip().lower()
        unit_b = (obs_b.get("unit") or "").strip().lower()

        # Check unit compatibility
        is_safe = True
        flag_reason = None
        if unit_a and unit_b and unit_a != unit_b:
            is_safe = False
            flag_reason = f"Unit mismatch: Report A reported '{unit_a}' whereas Report B reported '{unit_b}'. Comparison is unsafe."

        # Parse numeric values (considering user corrections if present)
        val_a_str = obs_a.get("user_corrected_value") or obs_a.get("original_value") or "0"
        val_b_str = obs_b.get("user_corrected_value") or obs_b.get("original_value") or "0"

        try:
            val_a = float(val_a_str)
            val_b = float(val_b_str)
        except Exception:
            val_a = obs_a.get("standardized_value") or 0.0
            val_b = obs_b.get("standardized_value") or 0.0

        abs_change = round(val_b - val_a, 2)
        pct_change = round(((val_b - val_a) / val_a * 100), 1) if val_a != 0 else 0.0

        trend_dir = "STABLE"
        if abs_change > 0.05:
            trend_dir = "INCREASED"
        elif abs_change < -0.05:
            trend_dir = "DECREASED"

        # Reference range analysis
        ref_low = obs_b.get("reference_range_low") or obs_a.get("reference_range_low")
        ref_high = obs_b.get("reference_range_high") or obs_a.get("reference_range_high")
        ref_text = obs_b.get("reference_range_text") or obs_a.get("reference_range_text") or f"{ref_low}-{ref_high}"

        shift_status = "UNCHANGED"
        clinical_note = f"Observed change of {abs_change:+} {obs_b.get('unit', '')} between visits."

        if not is_safe:
            shift_status = "UNSAFE_COMPARISON"
            clinical_note = flag_reason or "Comparison flagged due to test methodology or unit incompatibility."
        elif ref_low is not None and ref_high is not None:
            # Check if previous was above range
            if val_a > ref_high:
                if val_b <= ref_high and val_b >= ref_low:
                    shift_status = "WITHIN_NORMAL"
                    clinical_note = f"Value shifted from above the reference range into the standard interval ({ref_text})."
                elif val_b < val_a:
                    shift_status = "CLOSER_TO_NORMAL"
                    clinical_note = f"Value moved closer to the upper reference limit ({ref_high}), but remains elevated."
                else:
                    shift_status = "FARTHER_FROM_NORMAL"
                    clinical_note = f"Value moved further above the upper reference limit ({ref_high})."
            elif val_a < ref_low:
                if val_b >= ref_low and val_b <= ref_high:
                    shift_status = "WITHIN_NORMAL"
                    clinical_note = f"Value shifted from below the reference range into the standard interval ({ref_text})."
                elif val_b > val_a:
                    shift_status = "CLOSER_TO_NORMAL"
                    clinical_note = f"Value moved closer to the lower reference limit ({ref_low}), but remains low."
                else:
                    shift_status = "FARTHER_FROM_NORMAL"
                    clinical_note = f"Value moved further below the lower reference limit ({ref_low})."
            else:
                # val_a was normal
                if val_b >= ref_low and val_b <= ref_high:
                    shift_status = "WITHIN_NORMAL"
                    clinical_note = "Value remains safely within the normal reference interval."
                else:
                    shift_status = "FARTHER_FROM_NORMAL"
                    clinical_note = f"Value moved outside the normal reference interval ({ref_text})."

        return ComparisonItem(
            test_name=test_name,
            unit=obs_b.get("unit") or obs_a.get("unit") or "",
            report_a_value=val_a,
            report_b_value=val_b,
            report_a_original=str(val_a_str),
            report_b_original=str(val_b_str),
            absolute_change=abs_change,
            percentage_change=pct_change,
            trend_direction=trend_dir,
            reference_range_text=ref_text,
            range_shift_status=shift_status,
            clinical_note=clinical_note,
            is_safe_comparison=is_safe,
            flag_reason=flag_reason
        )

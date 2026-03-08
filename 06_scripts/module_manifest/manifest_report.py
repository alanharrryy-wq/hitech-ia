from __future__ import annotations

def build_manifest_report(
    *,
    manifest_path: str,
    source_inference_report: str,
    manifest: dict,
    metadata: dict,
    warnings: list[str],
    validation_errors: list[str],
    diff_text: str,
    built_at: str,
) -> dict:
    return {
        "schema_version": "1.0",
        "built_at": built_at,
        "manifest_path": manifest_path,
        "source_inference_report": source_inference_report,
        "manifest": manifest,
        "metadata": metadata,
        "warnings": warnings,
        "validation_errors": validation_errors,
        "is_valid": len(validation_errors) == 0,
        "diff_preview": diff_text.splitlines()[:80],
    }

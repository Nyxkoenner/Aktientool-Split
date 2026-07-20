from pathlib import Path

import pandas as pd

from stock_explorer.services.report_service import CompanyReportService

TEXT = """
Geschäftsbericht 2025
Geschäftsmodell
Die Beispiel AG verkauft Software und Dienstleistungen.
Geschäftssegmente
Software 70%
Dienstleistungen 30%
Umsatz nach Regionen
Europa 60%
Nordamerika 40%
Wesentliche Risiken
Cyberangriffe und steigende Zinsen könnten das Geschäft belasten.
Chancenbericht
Wachstum durch neue Produkte und Expansion.
Lieferkette
Ein Schlüssellieferant liefert kritische Komponenten.
Marken
Beispiel Cloud
"""


def test_report_service_saves_snapshot_and_profile_data(tmp_path: Path) -> None:
    service = CompanyReportService(data_dir=tmp_path)
    bundle = service.analyze_upload("BSP.DE", "bericht.txt", TEXT.encode("utf-8"))

    snapshot_path = service.save_snapshot(bundle)
    assert (snapshot_path / "analysis.json").exists()
    assert (snapshot_path / "document.txt").exists()
    assert not service.list_snapshots("BSP.DE").empty

    segment_frame = service.segment_candidates(bundle)
    region_frame = service.region_candidates(bundle)
    assert service.save_segments("BSP.DE", segment_frame) >= 1
    assert service.save_regions("BSP.DE", region_frame) >= 1

    segments = pd.read_csv(tmp_path / "company_segments.csv")
    regions = pd.read_csv(tmp_path / "company_regions.csv")
    assert "Software" in segments["segment"].tolist()
    assert "Europa" in regions["region"].tolist()

    service.update_qualitative_profile("BSP.DE", bundle)
    profile = pd.read_csv(tmp_path / "company_profiles.csv")
    assert profile.iloc[0]["business_model"]
    assert "Cyber" in profile.iloc[0]["risks"]


def test_saved_snapshot_can_be_loaded(tmp_path: Path) -> None:
    service = CompanyReportService(data_dir=tmp_path)
    bundle = service.analyze_upload("ABC", "annual.txt", TEXT.encode("utf-8"))
    path = service.save_snapshot(bundle)

    restored = service.load_snapshot(path)
    assert restored.document.sha256 == bundle.document.sha256
    assert restored.analysis.fiscal_year == 2025

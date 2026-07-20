from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable


@dataclass(slots=True)
class TextFinding:
    category: str
    title: str
    evidence: str
    confidence: float
    page: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StructuredCandidate:
    label: str
    evidence: str
    confidence: float
    share_pct: float | None = None
    amount: float | None = None
    currency: str = ""
    fiscal_year: int | None = None
    page: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportAnalysis:
    report_type: str
    fiscal_year: int | None
    language: str
    summary: str
    coverage_pct: float
    sections: dict[str, str] = field(default_factory=dict)
    risks: list[TextFinding] = field(default_factory=list)
    opportunities: list[TextFinding] = field(default_factory=list)
    dependencies: list[TextFinding] = field(default_factory=list)
    segments: list[StructuredCandidate] = field(default_factory=list)
    regions: list[StructuredCandidate] = field(default_factory=list)
    brands_and_subsidiaries: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_type": self.report_type,
            "fiscal_year": self.fiscal_year,
            "language": self.language,
            "summary": self.summary,
            "coverage_pct": self.coverage_pct,
            "sections": self.sections,
            "risks": [item.to_dict() for item in self.risks],
            "opportunities": [item.to_dict() for item in self.opportunities],
            "dependencies": [item.to_dict() for item in self.dependencies],
            "segments": [item.to_dict() for item in self.segments],
            "regions": [item.to_dict() for item in self.regions],
            "brands_and_subsidiaries": list(self.brands_and_subsidiaries),
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ReportAnalysis:
        return cls(
            report_type=str(payload.get("report_type", "Unbekannt")),
            fiscal_year=_optional_int(payload.get("fiscal_year")),
            language=str(payload.get("language", "unknown")),
            summary=str(payload.get("summary", "")),
            coverage_pct=float(payload.get("coverage_pct", 0.0) or 0.0),
            sections={str(key): str(value) for key, value in dict(payload.get("sections", {})).items()},
            risks=[TextFinding(**item) for item in payload.get("risks", [])],
            opportunities=[TextFinding(**item) for item in payload.get("opportunities", [])],
            dependencies=[TextFinding(**item) for item in payload.get("dependencies", [])],
            segments=[StructuredCandidate(**item) for item in payload.get("segments", [])],
            regions=[StructuredCandidate(**item) for item in payload.get("regions", [])],
            brands_and_subsidiaries=[str(value) for value in payload.get("brands_and_subsidiaries", [])],
            warnings=[str(value) for value in payload.get("warnings", [])],
        )


SECTION_PATTERNS: dict[str, tuple[str, ...]] = {
    "business": (
        r"\bbusiness overview\b",
        r"\bdescription of (?:the )?business\b",
        r"\bcompany profile\b",
        r"\bgeschäftsmodell\b",
        r"\bgeschäftstätigkeit\b",
        r"\bunternehmensprofil\b",
    ),
    "segments": (
        r"\boperating segments?\b",
        r"\breportable segments?\b",
        r"\bsegment information\b",
        r"\bgeschäftssegmente?\b",
        r"\bsegmentberichterstattung\b",
    ),
    "regions": (
        r"\bgeographic(?:al)? information\b",
        r"\brevenue by (?:geography|region|country)\b",
        r"\bregional information\b",
        r"\bregionale aufteilung\b",
        r"\bumsatz nach region(?:en)?\b",
        r"\bgeografische informationen\b",
    ),
    "risks": (
        r"\brisk factors?\b",
        r"\bprincipal risks?\b",
        r"\bmaterial risks?\b",
        r"\brisikofaktoren\b",
        r"\bwesentliche risiken\b",
        r"\brisikobericht\b",
    ),
    "opportunities": (
        r"\bopportunities\b",
        r"\bgrowth strategy\b",
        r"\bstrategic priorities\b",
        r"\bchancenbericht\b",
        r"\bchancen und risiken\b",
        r"\bwachstumsstrategie\b",
    ),
    "dependencies": (
        r"\bsupply chain\b",
        r"\bkey customers?\b",
        r"\bcustomer concentration\b",
        r"\braw materials?\b",
        r"\blieferkette\b",
        r"\bkundenkonzentration\b",
        r"\brohstoffe\b",
    ),
    "brands": (
        r"\bbrands?\b",
        r"\bsubsidiaries\b",
        r"\bportfolio of brands\b",
        r"\bmarken\b",
        r"\btochtergesellschaften\b",
    ),
}

RISK_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Regulierung": ("regulat", "compliance", "sanction", "genehmigung", "gesetz", "kartell"),
    "Finanzen": ("liquidity", "debt", "interest rate", "refinanc", "credit", "verschuld", "zins"),
    "Markt": ("competition", "demand", "pricing", "market", "wettbewerb", "nachfrage", "preisdruck"),
    "Operativ": ("operational", "production", "capacity", "quality", "betrieb", "produktion", "qualität"),
    "Lieferkette": ("supply chain", "supplier", "raw material", "lieferkette", "lieferant", "rohstoff"),
    "Cyber": ("cyber", "data breach", "information security", "datenschutz", "it-sicherheit"),
    "Recht": ("litigation", "lawsuit", "legal proceeding", "klage", "rechtsstreit"),
    "Klima": ("climate", "environmental", "emission", "klima", "umwelt", "emission"),
}

OPPORTUNITY_KEYWORDS = (
    "opportunity",
    "growth",
    "expansion",
    "innovation",
    "market share",
    "efficiency",
    "chance",
    "wachstum",
    "expansion",
    "innovation",
    "marktanteil",
    "effizienz",
)

DEPENDENCY_KEYWORDS = (
    "supplier",
    "supply chain",
    "customer concentration",
    "key customer",
    "single source",
    "raw material",
    "lieferant",
    "lieferkette",
    "kundenkonzentration",
    "großkunde",
    "einzige quelle",
    "rohstoff",
)

REGION_WORDS = (
    "europe",
    "germany",
    "americas",
    "north america",
    "south america",
    "asia",
    "asia-pacific",
    "apac",
    "emea",
    "china",
    "united states",
    "international",
    "europa",
    "deutschland",
    "nordamerika",
    "südamerika",
    "asien",
    "rest der welt",
)

PERCENT_PATTERN = re.compile(r"(?<!\d)(\d{1,3}(?:[.,]\d{1,2})?)\s*%")
AMOUNT_PATTERN = re.compile(
    r"(?P<currency>USD|EUR|GBP|CHF|\$|€|£)?\s*"
    r"(?P<amount>\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d+)?)\s*"
    r"(?P<scale>billion|million|thousand|bn|mn|mio\.?|mrd\.?|tsd\.?)?",
    flags=re.IGNORECASE,
)


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def normalize_report_text(text: str) -> str:
    value = str(text or "").replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _detect_language(text: str) -> str:
    sample = f" {text[:30000].lower()} "
    german = sum(sample.count(token) for token in (" der ", " die ", " und ", " geschäft", " risiko"))
    english = sum(sample.count(token) for token in (" the ", " and ", " business", " risk", " company"))
    if german > english * 1.1:
        return "de"
    if english > german * 1.1:
        return "en"
    return "unknown"


def _detect_fiscal_year(text: str) -> int | None:
    patterns = (
        r"(?:annual report|geschäftsbericht|fiscal year|financial year|geschäftsjahr)[^\n]{0,60}?(20\d{2})",
        r"(?:year ended|jahr zum|zum 31\.)[^\n]{0,80}?(20\d{2})",
    )
    lower = text[:120000].lower()
    for pattern in patterns:
        match = re.search(pattern, lower, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    years = [int(value) for value in re.findall(r"\b(20\d{2})\b", text[:20000])]
    plausible = [year for year in years if 2000 <= year <= 2100]
    return max(plausible) if plausible else None


def _detect_report_type(text: str) -> str:
    sample = text[:40000].lower()
    if "form 20-f" in sample or "20-f" in sample:
        return "20-F"
    if "form 10-k" in sample or "10-k" in sample:
        return "10-K"
    if "annual report" in sample or "geschäftsbericht" in sample:
        return "Annual Report"
    return "Company Report"


def _heading_matches(line: str, patterns: Iterable[str]) -> bool:
    compact = re.sub(r"\s+", " ", line.strip().lower())
    if len(compact) > 180:
        return False
    return any(re.search(pattern, compact, flags=re.IGNORECASE) for pattern in patterns)


def extract_sections(text: str, max_chars: int = 18000) -> dict[str, str]:
    lines = text.splitlines()
    hits: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        for section, patterns in SECTION_PATTERNS.items():
            if _heading_matches(line, patterns):
                if not hits or hits[-1] != (index, section):
                    hits.append((index, section))
                break
    sections: dict[str, str] = {}
    for position, (start, section) in enumerate(hits):
        if section in sections:
            continue
        end = hits[position + 1][0] if position + 1 < len(hits) else min(len(lines), start + 650)
        content = "\n".join(lines[start : min(end, start + 650)]).strip()
        if content:
            sections[section] = content[:max_chars]
    return sections


def _sentences(text: str) -> list[str]:
    flattened = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9])|\s*[•▪●]\s*", flattened)
    return [part.strip(" -–—\t") for part in parts if 45 <= len(part.strip()) <= 700]


def _deduplicate_text_findings(findings: list[TextFinding], limit: int) -> list[TextFinding]:
    result: list[TextFinding] = []
    seen: set[str] = set()
    for finding in sorted(findings, key=lambda item: item.confidence, reverse=True):
        key = re.sub(r"\W+", " ", finding.evidence.lower())[:180]
        if key in seen:
            continue
        seen.add(key)
        result.append(finding)
        if len(result) >= limit:
            break
    return result


def _extract_risks(text: str, risk_section: str) -> list[TextFinding]:
    source = risk_section or text[:120000]
    findings: list[TextFinding] = []
    for sentence in _sentences(source):
        lower = sentence.lower()
        categories = [
            category for category, words in RISK_KEYWORDS.items() if any(word in lower for word in words)
        ]
        generic_risk = any(
            word in lower
            for word in ("risk", "could adversely", "may adversely", "risiko", "könnte", "gefährd")
        )
        if not categories and not generic_risk:
            continue
        category = categories[0] if categories else "Allgemein"
        confidence = 0.9 if risk_section and categories else 0.75 if categories else 0.58
        findings.append(
            TextFinding(category=category, title=category, evidence=sentence, confidence=confidence)
        )
    return _deduplicate_text_findings(findings, 18)


def _extract_theme_findings(
    text: str,
    section: str,
    keywords: tuple[str, ...],
    category: str,
    limit: int,
) -> list[TextFinding]:
    source = section or text[:100000]
    findings: list[TextFinding] = []
    for sentence in _sentences(source):
        lower = sentence.lower()
        matches = sum(1 for word in keywords if word in lower)
        if not matches:
            continue
        confidence = min(0.95, 0.58 + matches * 0.1 + (0.12 if section else 0.0))
        findings.append(
            TextFinding(category=category, title=category, evidence=sentence, confidence=confidence)
        )
    return _deduplicate_text_findings(findings, limit)


def _parse_number(raw: str) -> float | None:
    cleaned = raw.replace(" ", "")
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        tail = cleaned.rsplit(",", 1)[-1]
        cleaned = cleaned.replace(",", ".") if len(tail) <= 2 else cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _scaled_amount(match: re.Match[str]) -> tuple[float | None, str]:
    amount = _parse_number(match.group("amount") or "")
    scale = (match.group("scale") or "").lower().rstrip(".")
    factor = 1.0
    if scale in {"billion", "bn", "mrd"}:
        factor = 1e9
    elif scale in {"million", "mn", "mio"}:
        factor = 1e6
    elif scale in {"thousand", "tsd"}:
        factor = 1e3
    currency_raw = (match.group("currency") or "").upper()
    currency = {"$": "USD", "€": "EUR", "£": "GBP"}.get(currency_raw, currency_raw)
    return (amount * factor if amount is not None else None), currency


def _candidate_label(line: str, match_start: int) -> str:
    prefix = line[:match_start]
    prefix = re.sub(r"^[\s\-–—•▪●\d.)]+", "", prefix).strip(" :;|-")
    prefix = re.sub(r"\s+", " ", prefix)
    if 2 <= len(prefix) <= 100:
        return prefix
    words = re.findall(r"[A-Za-zÄÖÜäöüß][\w&/\- ]{1,80}", line[:match_start])
    return words[-1].strip() if words else ""


def _structured_candidates(
    section: str,
    *,
    fiscal_year: int | None,
    region_mode: bool,
) -> list[StructuredCandidate]:
    candidates: list[StructuredCandidate] = []
    for raw_line in section.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not 4 <= len(line) <= 260:
            continue
        percent_match = PERCENT_PATTERN.search(line)
        amount_matches = [
            match
            for match in AMOUNT_PATTERN.finditer(line)
            if match.group("scale") or match.group("currency")
        ]
        match_start = (
            percent_match.start() if percent_match else amount_matches[0].start() if amount_matches else -1
        )
        if match_start < 0:
            continue
        label = _candidate_label(line, match_start)
        if not label:
            continue
        lower_label = label.lower()
        is_region = any(word in lower_label for word in REGION_WORDS)
        if region_mode and not is_region and not any(word in line.lower() for word in REGION_WORDS):
            continue
        if not region_mode and is_region:
            continue
        share = _parse_number(percent_match.group(1)) if percent_match else None
        amount: float | None = None
        currency = ""
        if amount_matches:
            amount, currency = _scaled_amount(amount_matches[0])
        confidence = 0.62
        if percent_match:
            confidence += 0.13
        if amount_matches:
            confidence += 0.1
        if region_mode and is_region:
            confidence += 0.08
        candidates.append(
            StructuredCandidate(
                label=label,
                evidence=line,
                confidence=min(confidence, 0.95),
                share_pct=share,
                amount=amount,
                currency=currency,
                fiscal_year=fiscal_year,
            )
        )
    deduped: list[StructuredCandidate] = []
    seen: set[str] = set()
    for item in sorted(candidates, key=lambda candidate: candidate.confidence, reverse=True):
        key = re.sub(r"\W+", "", item.label.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= 25:
            break
    return deduped


def _extract_names(section: str) -> list[str]:
    names: list[str] = []
    for line in section.splitlines():
        compact = re.sub(r"\s+", " ", line).strip(" -–—•▪●\t")
        if not 2 <= len(compact) <= 90:
            continue
        if any(character.isdigit() for character in compact) and len(re.findall(r"\d", compact)) > 3:
            continue
        if compact.lower() in {"brands", "brand", "marken", "subsidiaries", "tochtergesellschaften"}:
            continue
        if compact.count(" ") <= 8:
            names.append(compact)
    seen: set[str] = set()
    result: list[str] = []
    for name in names:
        key = re.sub(r"\W+", "", name.lower())
        if key and key not in seen:
            seen.add(key)
            result.append(name)
        if len(result) >= 30:
            break
    return result


def _summary(text: str, business_section: str) -> str:
    source = business_section or text[:9000]
    paragraphs = [re.sub(r"\s+", " ", paragraph).strip() for paragraph in source.split("\n\n")]
    useful = [paragraph for paragraph in paragraphs if 100 <= len(paragraph) <= 2500]
    if not useful:
        sentences = _sentences(source)
        return " ".join(sentences[:4])[:1600]
    return "\n\n".join(useful[:3])[:1800]


def analyze_report_text(text: str) -> ReportAnalysis:
    normalized = normalize_report_text(text)
    sections = extract_sections(normalized)
    fiscal_year = _detect_fiscal_year(normalized)
    risks = _extract_risks(normalized, sections.get("risks", ""))
    opportunities = _extract_theme_findings(
        normalized,
        sections.get("opportunities", ""),
        OPPORTUNITY_KEYWORDS,
        "Chance",
        12,
    )
    dependencies = _extract_theme_findings(
        normalized,
        sections.get("dependencies", ""),
        DEPENDENCY_KEYWORDS,
        "Abhängigkeit",
        12,
    )
    segment_section = sections.get("segments", "")
    region_section = sections.get("regions", "")
    segments = _structured_candidates(segment_section, fiscal_year=fiscal_year, region_mode=False)
    regions = _structured_candidates(region_section, fiscal_year=fiscal_year, region_mode=True)
    brands = _extract_names(sections.get("brands", ""))
    coverage_checks = [
        bool(sections.get("business")),
        bool(risks),
        bool(opportunities),
        bool(dependencies),
        bool(segments),
        bool(regions),
        bool(brands),
        fiscal_year is not None,
    ]
    warnings: list[str] = []
    if len(normalized) < 3000:
        warnings.append("Sehr wenig extrahierter Text; der Bericht könnte gescannt oder geschützt sein.")
    if not sections:
        warnings.append("Keine eindeutigen Abschnittsüberschriften erkannt.")
    if not segments and not regions:
        warnings.append("Keine belastbaren Segment- oder Regionskandidaten erkannt; manuelle Prüfung nötig.")
    return ReportAnalysis(
        report_type=_detect_report_type(normalized),
        fiscal_year=fiscal_year,
        language=_detect_language(normalized),
        summary=_summary(normalized, sections.get("business", "")),
        coverage_pct=round(sum(coverage_checks) / len(coverage_checks) * 100.0, 1),
        sections=sections,
        risks=risks,
        opportunities=opportunities,
        dependencies=dependencies,
        segments=segments,
        regions=regions,
        brands_and_subsidiaries=brands,
        warnings=warnings,
    )

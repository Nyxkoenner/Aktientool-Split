from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import urlparse

import pandas as pd

from .news_analysis import normalize_text

SOURCE_KIND_SCORES: dict[str, int] = {
    "official": 100,
    "regulator": 100,
    "sec": 100,
    "official_ir": 95,
    "ir": 95,
    "manual_confirmed": 90,
    "established_news": 80,
    "global": 70,
    "data_provider": 65,
    "provider": 65,
    "search_fallback": 45,
    "aggregator": 45,
    "unknown": 35,
}

OFFICIAL_DOMAINS = {
    "sec.gov",
    "bafin.de",
    "bundeskartellamt.de",
    "europa.eu",
    "ec.europa.eu",
    "fda.gov",
    "justice.gov",
}

ESTABLISHED_DOMAINS = {
    "reuters.com",
    "bloomberg.com",
    "ft.com",
    "wsj.com",
    "cnbc.com",
    "handelsblatt.com",
    "tagesschau.de",
    "faz.net",
    "sueddeutsche.de",
    "finanzen.net",
    "onvista.de",
    "marketwatch.com",
}

EVENT_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("profit_warning", ("gewinnwarnung", "profit warning")),
    ("guidance_down", ("prognose gesenkt", "guidance cut", "cuts guidance", "outlook lowered")),
    ("guidance_up", ("prognose angehoben", "guidance raised", "raises guidance", "outlook raised")),
    ("dividend_cut", ("dividende gekurzt", "dividend cut", "dividend suspended", "dividende ausgesetzt")),
    ("dividend_increase", ("dividende erhoht", "dividend increase", "dividend raised")),
    ("buyback", ("aktienruckkauf", "share buyback", "repurchase program")),
    ("analyst_downgrade", ("downgrade", "herabgestuft", "price target cut", "kursziel gesenkt")),
    ("analyst_upgrade", ("upgrade", "hochgestuft", "price target raised", "kursziel angehoben")),
    ("capital_raise", ("kapitalerhohung", "capital increase", "share offering", "rights issue", "dilution")),
    ("refinancing", ("refinanzierung", "refinancing", "bond issue", "anleihe platziert")),
    ("m_and_a", ("ubernahme", "acquisition", "merger", "takeover", "beteiligung erworben")),
    ("management_change", ("vorstand wechselt", "ceo resigns", "ceo appointed", "management change")),
    ("legal_regulatory", ("klage", "lawsuit", "investigation", "untersuchung", "regulator", "kartell")),
    ("layoffs", ("stellenabbau", "layoffs", "job cuts", "workforce reduction")),
    ("product_approval", ("zulassung", "approval", "approved by", "produktfreigabe")),
    ("insider_transaction", ("insiderkauf", "insider sale", "insider purchase", "director dealing")),
    ("capital_markets_day", ("capital markets day", "investor day", "kapitalmarkttag")),
    ("annual_meeting", ("hauptversammlung", "annual general meeting", "annual meeting", " agm ")),
    ("earnings", ("quartalszahlen", "quarterly results", "earnings", "jahreszahlen", "full year results")),
    ("sec_filing", ("10-k", "10-q", "8-k", "20-f", "6-k", "sec filing")),
    ("report", ("geschaftsbericht", "annual report", "halbjahresbericht", "interim report")),
)

POSITIVE_IMPACT: dict[str, int] = {
    "guidance raised": 5,
    "raises guidance": 5,
    "prognose angehoben": 5,
    "beats expectations": 4,
    "erwartungen ubertroffen": 4,
    "dividend increase": 4,
    "dividende erhoht": 4,
    "share buyback": 4,
    "aktienruckkauf": 4,
    "approval": 3,
    "zulassung": 3,
    "contract win": 3,
    "auftrag gewonnen": 3,
    "debt reduced": 3,
    "verschuldung gesenkt": 3,
    "cost savings": 2,
    "kosteneinsparungen": 2,
    "margin improved": 3,
    "marge verbessert": 3,
}

NEGATIVE_IMPACT: dict[str, int] = {
    "profit warning": 6,
    "gewinnwarnung": 6,
    "guidance cut": 5,
    "cuts guidance": 5,
    "prognose gesenkt": 5,
    "dividend cut": 5,
    "dividende gekurzt": 5,
    "dividend suspended": 6,
    "misses expectations": 4,
    "erwartungen verfehlt": 4,
    "capital increase": 4,
    "kapitalerhohung": 4,
    "rights issue": 4,
    "dilution": 3,
    "lawsuit": 3,
    "klage": 3,
    "investigation": 3,
    "untersuchung": 3,
    "bankruptcy": 7,
    "insolvenz": 7,
    "weak demand": 3,
    "schwache nachfrage": 3,
    "margin decline": 3,
    "marge gesunken": 3,
}


@dataclass(frozen=True, slots=True)
class SourceAssessment:
    score: int
    label: str
    reason: str


@dataclass(frozen=True, slots=True)
class ImpactAssessment:
    score: int
    label: str
    confidence: str
    reason: str


def _domain(link: str) -> str:
    try:
        host = urlparse(str(link or "")).hostname or ""
    except ValueError:
        host = ""
    host = host.casefold().removeprefix("www.")
    return host


def _domain_matches(host: str, domains: Iterable[str]) -> bool:
    return any(host == domain or host.endswith(f".{domain}") for domain in domains)


def assess_source(*, source: str, source_kind: str, link: str) -> SourceAssessment:
    normalized_kind = str(source_kind or "unknown").strip().casefold()
    normalized_source = normalize_text(source)
    host = _domain(link)

    if _domain_matches(host, OFFICIAL_DOMAINS) or "sec edgar" in normalized_source:
        return SourceAssessment(100, "offiziell", "Behorde oder regulatorische Originalquelle")
    if normalized_kind in {"official", "regulator", "sec"}:
        return SourceAssessment(100, "offiziell", "Als offizielle Quelle klassifiziert")
    if normalized_kind in {"official_ir", "ir"} or "investor relations" in normalized_source:
        return SourceAssessment(95, "unternehmens-ir", "Offizielle Investor-Relations-Quelle")
    if _domain_matches(host, ESTABLISHED_DOMAINS):
        return SourceAssessment(82, "etablierte nachrichtenquelle", f"Etablierte Quelle: {host}")

    score = SOURCE_KIND_SCORES.get(normalized_kind, SOURCE_KIND_SCORES["unknown"])
    if "google news" in normalized_source:
        score = min(score, 45)
        label = "suchaggregator"
        reason = "Google News verweist auf eine Drittquelle; Originalquelle prufen"
    elif score >= 75:
        label = "etablierte nachrichtenquelle"
        reason = "Direkter Nachrichtenfeed mit hoherem Quellenvertrauen"
    elif score >= 60:
        label = "datenanbieter"
        reason = "Datenanbieter oder allgemeiner Finanzfeed"
    elif score >= 40:
        label = "suchaggregator"
        reason = "Such- oder Aggregatorquelle"
    else:
        label = "unsichere quelle"
        reason = "Quelle konnte nicht eindeutig eingeordnet werden"
    return SourceAssessment(score, label, reason)


def classify_detailed_event(title: str, summary: str = "", fallback: str = "news") -> str:
    normalized = f" {normalize_text(f'{title} {summary}')} "
    for event_type, phrases in EVENT_RULES:
        if any(f" {normalize_text(phrase)} " in normalized for phrase in phrases):
            return event_type
    return str(fallback or "news")


def assess_stock_impact(title: str, summary: str = "", tone_label: str = "neutral") -> ImpactAssessment:
    title_text = normalize_text(title)
    summary_text = normalize_text(summary)
    positive = 0
    negative = 0
    positive_hits: list[str] = []
    negative_hits: list[str] = []

    for phrase, weight in POSITIVE_IMPACT.items():
        normalized_phrase = normalize_text(phrase)
        if normalized_phrase in title_text:
            positive += weight * 2
            positive_hits.append(phrase)
        elif normalized_phrase in summary_text:
            positive += weight
            positive_hits.append(phrase)
    for phrase, weight in NEGATIVE_IMPACT.items():
        normalized_phrase = normalize_text(phrase)
        if normalized_phrase in title_text:
            negative += weight * 2
            negative_hits.append(phrase)
        elif normalized_phrase in summary_text:
            negative += weight
            negative_hits.append(phrase)

    score = max(-10, min(10, positive - negative))
    if positive >= 3 and negative >= 3:
        label = "gemischt"
    elif score >= 2:
        label = "positiv"
    elif score <= -2:
        label = "negativ"
    else:
        label = "unklar"

    strongest = max(positive, negative)
    confidence = "hoch" if strongest >= 8 else "mittel" if strongest >= 4 else "niedrig"
    reasons: list[str] = []
    if positive_hits:
        reasons.append("Positiv: " + ", ".join(dict.fromkeys(positive_hits[:3])))
    if negative_hits:
        reasons.append("Negativ: " + ", ".join(dict.fromkeys(negative_hits[:3])))
    if not reasons:
        reasons.append(
            "Keine eindeutige Aktienwirkungs-Phrase erkannt; Nachrichtenton "
            f"ist {str(tone_label or 'neutral').lower()}."
        )
    return ImpactAssessment(score, label, confidence, " | ".join(reasons))


def _token_set(value: str) -> set[str]:
    stopwords = {
        "der",
        "die",
        "das",
        "und",
        "mit",
        "von",
        "fur",
        "the",
        "and",
        "for",
        "with",
        "from",
        "aktie",
        "stock",
        "news",
    }
    return {token for token in normalize_text(value).split() if len(token) >= 3 and token not in stopwords}


def _similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _stable_cluster_id(ticker: str, event_type: str, date_value: pd.Timestamp, title: str) -> str:
    normalized_title = " ".join(sorted(_token_set(title))[:12])
    raw = f"{ticker}|{event_type}|{date_value.date().isoformat()}|{normalized_title}"
    return hashlib.sha1(raw.encode("utf-8"), usedforsecurity=False).hexdigest()[:16]


def enrich_news_intelligence(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    result = frame.copy()
    for column, default in {
        "summary": "",
        "source": "",
        "source_kind": "unknown",
        "link": "",
        "sentiment_label": "neutral",
        "event_type": "news",
        "relevance_score": 0,
    }.items():
        if column not in result.columns:
            result[column] = default

    result["published"] = pd.to_datetime(result.get("published"), errors="coerce")
    rows: list[dict[str, Any]] = []
    for _, row in result.iterrows():
        title = str(row.get("title") or "")
        summary = str(row.get("summary") or "")
        source_assessment = assess_source(
            source=str(row.get("source") or ""),
            source_kind=str(row.get("source_kind") or "unknown"),
            link=str(row.get("link") or ""),
        )
        event_type = classify_detailed_event(title, summary, str(row.get("event_type") or "news"))
        impact = assess_stock_impact(title, summary, str(row.get("sentiment_label") or "neutral"))
        output = row.to_dict()
        output.update(
            {
                "event_type_v2": event_type,
                "tone_label": str(row.get("sentiment_label") or "neutral").lower(),
                "impact_score": impact.score,
                "impact_label": impact.label,
                "impact_confidence": impact.confidence,
                "impact_reason": impact.reason,
                "source_trust_score": source_assessment.score,
                "source_quality": source_assessment.label,
                "source_trust_reason": source_assessment.reason,
            }
        )
        rows.append(output)
    return pd.DataFrame(rows)


def cluster_news(
    frame: pd.DataFrame,
    *,
    max_days: int = 3,
    similarity_threshold: float = 0.48,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    enriched = enrich_news_intelligence(frame)
    if enriched.empty:
        return enriched, pd.DataFrame()

    enriched = enriched.dropna(subset=["published", "title"]).copy()
    enriched = enriched.sort_values("published", ascending=True).reset_index(drop=True)
    clusters: list[dict[str, Any]] = []
    memberships: list[int] = []

    for _, row in enriched.iterrows():
        published = pd.Timestamp(row["published"])
        tokens = _token_set(str(row.get("title") or ""))
        event_type = str(row.get("event_type_v2") or "news")
        selected_index: int | None = None
        selected_similarity = 0.0
        for cluster_index, cluster in enumerate(clusters):
            date_delta = abs((published.normalize() - cluster["last_date"].normalize()).days)
            if date_delta > max_days:
                continue
            if event_type != cluster["event_type"] and "news" not in {event_type, cluster["event_type"]}:
                continue
            similarity = _similarity(tokens, cluster["tokens"])
            same_link = bool(row.get("link")) and str(row.get("link")) in cluster["links"]
            same_event_day = date_delta <= 1 and event_type == cluster["event_type"] and similarity >= 0.08
            if same_link or similarity >= similarity_threshold or same_event_day:
                if same_link or similarity > selected_similarity or same_event_day:
                    selected_index = cluster_index
                    selected_similarity = 1.0 if same_link else similarity
        if selected_index is None:
            clusters.append(
                {
                    "first_date": published,
                    "last_date": published,
                    "event_type": event_type,
                    "tokens": set(tokens),
                    "members": [],
                    "links": set(),
                }
            )
            selected_index = len(clusters) - 1
        cluster = clusters[selected_index]
        cluster["members"].append(int(row.name))
        cluster["last_date"] = max(cluster["last_date"], published)
        cluster["tokens"].update(tokens)
        if row.get("link"):
            cluster["links"].add(str(row.get("link")))
        memberships.append(selected_index)

    enriched["_cluster_index"] = memberships
    cluster_rows: list[dict[str, Any]] = []
    cluster_id_by_index: dict[int, str] = {}
    for cluster_index, cluster in enumerate(clusters):
        members = enriched.loc[enriched["_cluster_index"] == cluster_index].copy()
        members = members.sort_values(
            ["source_trust_score", "relevance_score", "published"],
            ascending=[False, False, False],
        )
        primary = members.iloc[0]
        event_type = str(primary.get("event_type_v2") or cluster["event_type"])
        cluster_id = _stable_cluster_id(
            str(primary.get("ticker_yahoo") or ""),
            event_type,
            pd.Timestamp(cluster["first_date"]),
            str(primary.get("title") or ""),
        )
        cluster_id_by_index[cluster_index] = cluster_id
        sources = sorted({str(value) for value in members["source"].dropna() if str(value).strip()})
        links = [str(value) for value in members["link"].dropna() if str(value).strip()]
        trust_values = pd.to_numeric(members["source_trust_score"], errors="coerce").dropna()
        impact_values = pd.to_numeric(members["impact_score"], errors="coerce").dropna()
        tone_counts = members["tone_label"].fillna("neutral").astype(str).value_counts()
        impact_counts = members["impact_label"].fillna("unklar").astype(str).value_counts()
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "ticker_yahoo": primary.get("ticker_yahoo", ""),
                "published": members["published"].min(),
                "last_seen": members["published"].max(),
                "title": primary.get("title", ""),
                "summary": str(primary.get("summary") or "")[:800],
                "event_type": event_type,
                "tone_label": str(tone_counts.index[0]) if not tone_counts.empty else "neutral",
                "impact_label": str(impact_counts.index[0]) if not impact_counts.empty else "unklar",
                "impact_score": float(impact_values.mean()) if not impact_values.empty else 0.0,
                "impact_confidence": primary.get("impact_confidence", "niedrig"),
                "impact_reason": primary.get("impact_reason", ""),
                "source_trust_score": int(trust_values.max()) if not trust_values.empty else 0,
                "source_quality": primary.get("source_quality", "unsichere quelle"),
                "primary_source": primary.get("source", ""),
                "primary_link": primary.get("link", ""),
                "source_count": len(sources),
                "article_count": len(members),
                "sources": " | ".join(sources),
                "links": " | ".join(dict.fromkeys(links)),
                "relevance_score": float(
                    pd.to_numeric(members["relevance_score"], errors="coerce").fillna(0).max()
                ),
            }
        )

    enriched["cluster_id"] = enriched["_cluster_index"].map(cluster_id_by_index)
    enriched = enriched.drop(columns=["_cluster_index"])
    cluster_frame = (
        pd.DataFrame(cluster_rows).sort_values("published", ascending=False).reset_index(drop=True)
    )
    return enriched.sort_values("published", ascending=False).reset_index(drop=True), cluster_frame


def source_health_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame(columns=["source_quality", "articles", "sources", "average_trust"])
    data = frame.copy()
    data["source_trust_score"] = pd.to_numeric(data.get("source_trust_score"), errors="coerce")
    return (
        data.groupby("source_quality", dropna=False)
        .agg(
            articles=("title", "count"),
            sources=("source", "nunique"),
            average_trust=("source_trust_score", "mean"),
        )
        .reset_index()
        .sort_values("average_trust", ascending=False)
    )


def confidence_from_sample(count: int) -> str:
    if count >= 20:
        return "hoch"
    if count >= 8:
        return "mittel"
    if count >= 3:
        return "gering"
    return "sehr gering"


def safe_percentage(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None

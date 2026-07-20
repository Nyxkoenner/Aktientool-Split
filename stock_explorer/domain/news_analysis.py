from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd

COMPANY_SUFFIXES = re.compile(
    r"\b(ag|se|sa|s\.a\.|plc|n\.v\.|gmbh|kgaa|inc\.?|corp\.?|corporation|ltd\.?|limited|holdings?)\b",
    flags=re.IGNORECASE,
)

FINANCE_CONTEXT_TERMS = {
    "aktie",
    "stock",
    "shares",
    "investor",
    "investoren",
    "boerse",
    "börse",
    "earnings",
    "quartalszahlen",
    "quarterly results",
    "umsatz",
    "revenue",
    "gewinn",
    "profit",
    "dividende",
    "dividend",
    "kursziel",
    "price target",
    "analyst",
    "prognose",
    "guidance",
    "cashflow",
    "free cash flow",
    "jahresbericht",
    "annual report",
    "hauptversammlung",
    "annual meeting",
}

POSITIVE_PHRASES: dict[str, int] = {
    "erwartungen uebertroffen": 4,
    "erwartungen übertroffen": 4,
    "beats expectations": 4,
    "beat expectations": 4,
    "prognose angehoben": 4,
    "raises guidance": 4,
    "raised guidance": 4,
    "dividende erhoeht": 4,
    "dividende erhöht": 4,
    "dividend increase": 4,
    "dividend raised": 4,
    "aktienrueckkauf": 3,
    "aktienrückkauf": 3,
    "share buyback": 3,
    "upgrade": 3,
    "hochgestuft": 3,
    "kursziel angehoben": 3,
    "price target raised": 3,
    "verschuldung gesenkt": 3,
    "debt reduced": 3,
    "rekordumsatz": 3,
    "record revenue": 3,
    "marge verbessert": 3,
    "margin improved": 3,
    "auftrag gewonnen": 2,
    "contract win": 2,
}

NEGATIVE_PHRASES: dict[str, int] = {
    "gewinnwarnung": 5,
    "profit warning": 5,
    "prognose gesenkt": 4,
    "cuts guidance": 4,
    "cut guidance": 4,
    "dividende gekuerzt": 5,
    "dividende gekürzt": 5,
    "dividend cut": 5,
    "dividende ausgesetzt": 5,
    "dividend suspended": 5,
    "erwartungen verfehlt": 4,
    "misses expectations": 4,
    "missed expectations": 4,
    "downgrade": 3,
    "herabgestuft": 3,
    "kursziel gesenkt": 3,
    "price target cut": 3,
    "klage": 3,
    "lawsuit": 3,
    "untersuchung": 3,
    "investigation": 3,
    "betrug": 5,
    "fraud": 5,
    "insolvenz": 5,
    "bankruptcy": 5,
    "marge gesunken": 3,
    "margin decline": 3,
    "stellenabbau": 2,
    "layoffs": 2,
}

EVENT_PHRASES: list[tuple[str, tuple[str, ...]]] = [
    (
        "earnings",
        (
            "quartalszahlen",
            "quartalsbericht",
            "quarterly results",
            "quarterly earnings",
            "earnings release",
            "full year results",
            "jahreszahlen",
            "halbjahreszahlen",
            "half year results",
        ),
    ),
    (
        "dividend",
        (
            "ex dividend",
            "ex dividende",
            "dividend payment",
            "dividendenzahlung",
            "dividend increase",
            "dividend cut",
            "dividende",
            "dividend",
        ),
    ),
    (
        "annual_meeting",
        ("hauptversammlung", "annual general meeting", "annual meeting", "agm"),
    ),
    (
        "capital_markets_day",
        ("capital markets day", "capital market day", "investor day", "kapitalmarkttag"),
    ),
    (
        "conference",
        ("investor conference", "investorenkonferenz", "conference presentation"),
    ),
    (
        "report",
        (
            "geschaeftsbericht",
            "geschäftsbericht",
            "annual report",
            "sustainability report",
            "nachhaltigkeitsbericht",
        ),
    ),
    (
        "analyst",
        (
            "analyst",
            "analysten",
            "kursziel",
            "price target",
            "rating",
            "upgrade",
            "downgrade",
            "outperform",
            "underperform",
        ),
    ),
]


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = text.casefold().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def clean_ticker(value: Any) -> str:
    return str(value or "").strip().upper().replace("$", "")


def default_aliases(company_name: str, ticker: str, extra_aliases: Iterable[str] = ()) -> list[str]:
    company = str(company_name or "").strip()
    simplified = COMPANY_SUFFIXES.sub("", company).strip(" ,-.")
    ticker_base = clean_ticker(ticker).split(".")[0]
    candidates = [company, simplified, *extra_aliases]
    if normalize_text(ticker_base) == normalize_text(simplified):
        candidates.append(ticker_base)
    candidates.extend(part for part in simplified.split() if len(normalize_text(part)) >= 5)

    aliases: dict[str, str] = {}
    for candidate in candidates:
        raw = str(candidate or "").strip()
        normalized = normalize_text(raw)
        if len(normalized) < 3:
            continue
        aliases.setdefault(normalized, raw)
    return sorted(aliases.values(), key=lambda item: len(normalize_text(item)), reverse=True)


def primary_query_alias(company_name: str, ticker: str, extra_aliases: Iterable[str] = ()) -> str:
    aliases = default_aliases(company_name, ticker, extra_aliases)
    if not aliases:
        return str(company_name or clean_ticker(ticker)).strip()
    multiword = [alias for alias in aliases if len(normalize_text(alias).split()) >= 2]
    return max(multiword or aliases, key=lambda item: len(normalize_text(item)))


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = f" {normalize_text(text)} "
    normalized_phrase = normalize_text(phrase)
    return bool(normalized_phrase and f" {normalized_phrase} " in normalized_text)


def _matched_alias(text: str, aliases: Iterable[str]) -> str | None:
    normalized_text = f" {normalize_text(text)} "
    for alias in sorted(set(aliases), key=lambda item: len(normalize_text(item)), reverse=True):
        normalized_alias = normalize_text(alias)
        if normalized_alias and f" {normalized_alias} " in normalized_text:
            return alias
    return None


@dataclass(frozen=True, slots=True)
class SentimentResult:
    score: int
    label: str
    confidence: str
    reason: str


@dataclass(frozen=True, slots=True)
class RelevanceResult:
    matched_alias: str
    score: int
    label: str
    reason: str
    is_relevant: bool


class NewsAnalyzer:
    def aliases(self, company_name: str, ticker: str, extra_aliases: Iterable[str] = ()) -> list[str]:
        return default_aliases(company_name, ticker, extra_aliases)

    def relevance(
        self,
        *,
        title: str,
        summary: str,
        company_name: str,
        ticker: str,
        source_kind: str,
        extra_aliases: Iterable[str] = (),
    ) -> RelevanceResult:
        aliases = self.aliases(company_name, ticker, extra_aliases)
        title_alias = _matched_alias(title, aliases)
        summary_alias = _matched_alias(summary, aliases)
        matched = title_alias or summary_alias
        score = 0
        reasons: list[str] = []

        if matched:
            alias_length = len(normalize_text(matched))
            if title_alias:
                score = 82 if alias_length >= 5 else 52
                reasons.append("Firmenalias im Titel")
            else:
                score = 64 if alias_length >= 5 else 38
                reasons.append("Firmenalias in der Beschreibung")

        combined = f"{title} {summary}"
        context_hits = [term for term in FINANCE_CONTEXT_TERMS if _contains_phrase(combined, term)]
        if context_hits:
            score += min(20, len(set(context_hits)) * 7)
            if title_alias and len(normalize_text(title_alias)) < 5:
                score += 12
            reasons.append("Finanz-/Unternehmenskontext: " + ", ".join(sorted(set(context_hits))[:4]))

        if source_kind == "search_fallback" and not matched:
            score = min(score, 20)
            reasons.append("nur Suchabfrage, kein sichtbarer Firmenalias")

        score = max(0, min(100, score))
        label = "hoch" if score >= 85 else "mittel" if score >= 70 else "niedrig"
        return RelevanceResult(
            matched_alias=matched or "–",
            score=score,
            label=label,
            reason=" · ".join(reasons) if reasons else "kein ausreichend eindeutiger Firmenbezug",
            is_relevant=score >= 70,
        )

    def sentiment(self, title: str, summary: str = "") -> SentimentResult:
        positive_points = 0
        negative_points = 0
        positive_hits: list[str] = []
        negative_hits: list[str] = []

        for phrase, weight in POSITIVE_PHRASES.items():
            if _contains_phrase(title, phrase):
                positive_points += weight * 2
                positive_hits.append(phrase)
            elif summary and _contains_phrase(summary, phrase):
                positive_points += weight
                positive_hits.append(phrase)

        for phrase, weight in NEGATIVE_PHRASES.items():
            if _contains_phrase(title, phrase):
                negative_points += weight * 2
                negative_hits.append(phrase)
            elif summary and _contains_phrase(summary, phrase):
                negative_points += weight
                negative_hits.append(phrase)

        raw_score = max(-10, min(10, positive_points - negative_points))
        if positive_points >= 2 and negative_points >= 2:
            label = "gemischt"
        elif raw_score >= 2:
            label = "positiv"
        elif raw_score <= -2:
            label = "negativ"
        else:
            label = "neutral"

        strongest = max(positive_points, negative_points)
        if label == "gemischt" and min(positive_points, negative_points) >= 4:
            confidence = "hoch"
        elif strongest >= 6:
            confidence = "hoch"
        elif strongest >= 3:
            confidence = "mittel"
        else:
            confidence = "niedrig"

        reason_parts: list[str] = []
        if positive_hits:
            reason_parts.append("Positiv: " + ", ".join(dict.fromkeys(positive_hits[:3])))
        if negative_hits:
            reason_parts.append("Negativ: " + ", ".join(dict.fromkeys(negative_hits[:3])))
        reason = (
            " | ".join(reason_parts) if reason_parts else "Keine eindeutige richtungsweisende Phrase erkannt."
        )
        return SentimentResult(raw_score, label, confidence, reason)

    def classify_event(self, text: str) -> str:
        for event_type, phrases in EVENT_PHRASES:
            if any(_contains_phrase(text, phrase) for phrase in phrases):
                return event_type
        return "news"

    def enrich(
        self,
        frame: pd.DataFrame,
        *,
        ticker: str,
        company_name: str,
        extra_aliases: Iterable[str] = (),
        min_candidate_score: int = 35,
        relevant_score: int = 70,
        max_items: int = 80,
    ) -> pd.DataFrame:
        output_columns = [
            "published",
            "ticker_yahoo",
            "title",
            "link",
            "source",
            "source_kind",
            "matched_alias",
            "sentiment_score",
            "sentiment_label",
            "sentiment_confidence",
            "sentiment_reason",
            "event_type",
            "relevance_score",
            "relevance_label",
            "relevance_reason",
            "is_relevant",
        ]
        if frame is None or frame.empty:
            return pd.DataFrame(columns=output_columns)

        rows: list[dict[str, Any]] = []
        for _, entry in frame.iterrows():
            title = str(entry.get("title", "") or "")
            summary = str(entry.get("summary", "") or "")
            source_kind = str(entry.get("source_kind", "global") or "global")
            relevance = self.relevance(
                title=title,
                summary=summary,
                company_name=company_name,
                ticker=ticker,
                source_kind=source_kind,
                extra_aliases=extra_aliases,
            )
            if relevance.score < min_candidate_score:
                continue
            sentiment = self.sentiment(title, summary)
            rows.append(
                {
                    "published": entry.get("published"),
                    "ticker_yahoo": clean_ticker(ticker),
                    "title": title,
                    "link": str(entry.get("link", "") or ""),
                    "source": str(entry.get("source", "") or ""),
                    "source_kind": source_kind,
                    "matched_alias": relevance.matched_alias,
                    "sentiment_score": sentiment.score,
                    "sentiment_label": sentiment.label,
                    "sentiment_confidence": sentiment.confidence,
                    "sentiment_reason": sentiment.reason,
                    "event_type": self.classify_event(f"{title} {summary}")
                    if relevance.score >= relevant_score
                    else "news",
                    "relevance_score": relevance.score,
                    "relevance_label": relevance.label,
                    "relevance_reason": relevance.reason,
                    "is_relevant": relevance.score >= relevant_score,
                }
            )

        result = pd.DataFrame(rows, columns=output_columns)
        if result.empty:
            return result
        result["published"] = pd.to_datetime(result["published"], errors="coerce")
        result = result.dropna(subset=["published", "title"])
        result["_dedupe"] = result["title"].map(normalize_text)
        result = (
            result.sort_values(["relevance_score", "published"], ascending=[False, False])
            .drop_duplicates("_dedupe", keep="first")
            .drop(columns="_dedupe")
            .sort_values("published", ascending=False)
            .head(max_items)
            .reset_index(drop=True)
        )
        return result

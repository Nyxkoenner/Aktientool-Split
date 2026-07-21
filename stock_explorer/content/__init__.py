"""Kuratiertes Lern- und Hilfematerial des Aktien Explorers."""

from .glossary import GLOSSARY, ExternalResource, GlossaryEntry, glossary_entry, search_glossary
from .page_guides import PAGE_GUIDES, PageGuide, page_guide

__all__ = [
    "ExternalResource",
    "GLOSSARY",
    "GlossaryEntry",
    "PAGE_GUIDES",
    "PageGuide",
    "glossary_entry",
    "page_guide",
    "search_glossary",
]

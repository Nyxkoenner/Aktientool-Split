from stock_explorer.domain.ux_preferences import (
    DEFAULT_KNOWLEDGE_LEVEL,
    KNOWLEDGE_SESSION_KEY,
    KnowledgeLevel,
    knowledge_level_from_state,
    normalize_knowledge_level,
    set_knowledge_level,
)


def test_knowledge_level_defaults_and_normalizes() -> None:
    assert normalize_knowledge_level(None) == DEFAULT_KNOWLEDGE_LEVEL
    assert normalize_knowledge_level("BEGINNER") == KnowledgeLevel.BEGINNER
    assert normalize_knowledge_level("expert") == KnowledgeLevel.EXPERT
    assert normalize_knowledge_level("unknown") == DEFAULT_KNOWLEDGE_LEVEL


def test_knowledge_level_uses_independent_application_state() -> None:
    state: dict[str, object] = {}
    selected = set_knowledge_level(KnowledgeLevel.BEGINNER, state)

    assert selected == KnowledgeLevel.BEGINNER
    assert state[KNOWLEDGE_SESSION_KEY] == "beginner"
    assert knowledge_level_from_state(state) == KnowledgeLevel.BEGINNER
    assert "knowledge_level_selector" not in state

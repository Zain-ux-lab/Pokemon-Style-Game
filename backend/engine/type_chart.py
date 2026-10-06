"""Move type versus defender type; Neutral supports legacy engine callers."""
STRONG_AGAINST = {'Magic': 'Physical', 'Physical': 'Spirit', 'Spirit': 'Magic'}


def effectiveness_percent(attack_type: str, defense_type: str) -> int:
    if STRONG_AGAINST.get(attack_type) == defense_type:
        return 125
    if STRONG_AGAINST.get(defense_type) == attack_type:
        return 80
    return 100

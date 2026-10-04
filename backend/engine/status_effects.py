"""Visible conditions, measured in their holder's normal actions."""
from dataclasses import dataclass


@dataclass
class Status:
    turns: int
    slot: int | None = None


DURATIONS = {'spores': 2, 'thorns': 1, 'mark': 2, 'paralyse': 1,
             'confuse': 2, 'weaken': 2, 'expose': 2, 'echo': 1}

DESCRIPTIONS = {
    'echo': 'Deal 10 delayed damage after your next action; either character switching cancels it.',
    'spores': 'For two actions, damaging moves cause 6 recoil. Switching clears it.',
    'drain': 'Recover half the direct HP damage dealt, rounded down.',
    'thorns': 'Reflect 14 damage from contact hits until after your next action.',
    'mark': 'Mark for two actions. Piercing Volley consumes the mark for +18 damage.',
    'exploit': 'Consume a mark for +18 damage.',
    'paralyse': 'Prevent voluntary switching for one action. Moves remain usable.',
    'reprisal': 'Add half the direct damage received last enemy action, capped at 15.',
    'dread': 'If the target starts below half HP, weaken its next attack by 25%.',
    'confuse': 'For two actions, the marked strongest attack causes 8 recoil.',
    'phase': 'Ignore and consume guard. Type resistance still applies.',
    'harvest': 'Consume spores for +10 damage, ending their ongoing pressure.',
    'weaken': 'Next damaging move deals 25% less damage; expires after two actions.',
    'expose': 'Next direct hit deals 25% more damage; expires after two actions.',
}

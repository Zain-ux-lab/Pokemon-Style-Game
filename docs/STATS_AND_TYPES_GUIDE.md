# BattleLab · Stats & Type Guide

**A quick reference for choosing your team and understanding damage.**
Current rules · 6 October 2026 · Numbers are provisional playtest values.

## 1. The three types

**✦ Magic beats ◆ Physical → Physical beats ◉ Spirit → Spirit beats Magic.**

Read the chart across: choose your **move’s type**, then the **enemy character’s type**.

| Move type ↓ / Enemy type → | ✦ Magic | ◆ Physical | ◉ Spirit |
| :--- | :---: | :---: | :---: |
| ✦ Magic | Normal · 100% | Strong · 125% | Resisted · 80% |
| ◆ Physical | Resisted · 80% | Normal · 100% | Strong · 125% |
| ◉ Spirit | Strong · 125% | Resisted · 80% | Normal · 100% |

**Strong:** 25% more damage. **Resisted:** 20% less damage. **Normal:** unchanged.

The move’s type determines the matchup—not the attacker’s character type.
Mage can use a Physical move; that move follows the Physical row.
There is no extra bonus simply for using a move matching your own character’s type.

---

## 2. What each stat means

| Stat | What it controls | When it matters |
| :--- | :--- | :--- |
| **HP** | How much health you have. At zero, the character is knocked out. | Staying alive; healing never exceeds maximum HP. |
| **Power** | Strength of Physical attacks. | Higher Power increases Physical damage. |
| **Focus** | Strength of Magic and Spirit attacks. | Higher Focus increases both kinds of damage. |
| **Armour** | Protection against Physical attacks. | Higher Armour reduces incoming Physical damage. |
| **Ward** | Protection against Magic and Spirit attacks. | Higher Ward reduces both kinds of incoming damage. |
| **Recovery** | Strength of healing, including drain healing. | 10 is the baseline; 12 gives 120% healing before caps. |

**Character Power and move power are different.** Character Power is a stat;
move power is the strength printed in that move’s definition. Both contribute to damage.
Contact is a separate move property: it can trigger retaliation, but does not decide
whether Power or Focus is used. There are currently no speed, critical-hit or energy stats.

---

## 3. All ten characters

Higher numbers strengthen the corresponding stat. These values show each character’s
starting maximum HP and permanent stats; temporary effects are separate.

| Character | Type | HP | Power | Focus | Armour | Ward | Recovery |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mage | ✦ Magic | 100 | 8 | 12 | 9 | 11 | 10 |
| Sporestag | ◆ Physical | 120 | 11 | 9 | 12 | 9 | 10 |
| Glowmire | ◉ Spirit | 90 | 7 | 11 | 8 | 11 | 10 |
| Bramblebelly | ◆ Physical | 120 | 11 | 8 | 12 | 9 | 10 |
| Veyne | ◆ Physical | 100 | 12 | 9 | 9 | 9 | 9 |
| Coil | ✦ Magic | 100 | 9 | 12 | 10 | 10 | 8 |
| Bastion | ◆ Physical | 120 | 10 | 8 | 13 | 11 | 8 |
| Vesperfang | ✦ Magic | 100 | 9 | 12 | 9 | 10 | 9 |
| Hushwing | ◉ Spirit | 90 | 8 | 10 | 8 | 12 | 12 |
| Riftclaw | ◉ Spirit | 100 | 11 | 11 | 9 | 9 | 8 |

---

## 4. Damage, step by step

**Physical:** move power × your Power ÷ enemy Armour.
**Magic / Spirit:** move power × your Focus ÷ enemy Ward.

Round down to get **base damage**. A damaging move starts with at least one base damage.
Then apply the type chart. Later modifiers—special ability bonuses, Weaken, Expose
and guard—can change the result further. Each calculation rounds down; damage cannot
remove more HP than the target has left. Phase attacks bypass guard.

### Example · Mage’s Arcane Bolt against Bastion

| Step | Calculation | Result |
| :--- | :--- | ---: |
| Base damage | Move power 22 × Mage Focus 12 ÷ Bastion Ward 11 | **24** |
| Type matchup | Magic against Physical: 24 × 1.25 | **30** |
| If Bastion has 30% guard | 30 × 0.70 | **21** |

Without other modifiers, the move deals **30 HP damage**, or **21 with guard**.
The move preview shows **24 base damage**. Base damage already accounts for character
stats; it is not simply the move’s power and it excludes type effectiveness.

---

## 5. Healing and drain

**Healing:** listed heal amount × Recovery ÷ 10, rounded down.

Hushwing’s Soft Wing lists 10 healing. With Recovery 12 it restores **12 HP**,
or less if Hushwing is missing fewer than 12 HP.

**Drain:** actual direct damage × Recovery ÷ 40, rounded down, capped at **4 HP**
and at the healer’s missing HP. It uses the damage actually dealt after reductions.

At Recovery 10, drain heals 25% of direct damage before the caps.
At Recovery 9, it heals 22.5%: 13 direct damage restores **2 HP**, not 3.
A full-health character receives no healing.

## Remember

- Check the **move’s type** against the **enemy character’s type**.
- Match your move to your stronger attacking stat—and the enemy’s weaker defence.
- Base damage is a starting point; effects and guard can alter the final HP loss.
- Switching spends your turn and clears effects. Replacing a knocked-out character is free.

*Verified against the current roster, type chart and damage calculations. Update this guide when balance changes.*

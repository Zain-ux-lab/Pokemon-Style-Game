"""Ten fixed identities. Numbers are initial playtest values, not final balance."""


def attack(name, power, damage_type, *, contact=False, mechanic=''):
    return dict(name=name, power=power, damage_type=damage_type, contact=contact, mechanic=mechanic)


def status(name, mechanic, damage_type='Magic'):
    return dict(name=name, effect='status', mechanic=mechanic, power=10, damage_type=damage_type)


def heal(name, amount):
    return dict(name=name, effect='heal', effect_amount=amount)


def guard(name, damage_type, *, contact=False):
    return dict(name=name, power=12, effect='guard', effect_amount=30, damage_type=damage_type, contact=contact)


ROSTER = [
    dict(id='mage', name='Mage', type='Magic', maxHp=100, art='Mage', moves=[
        attack('Arcane Bolt',22,'Magic'), attack('Staff Strike',20,'Physical',contact=True),
        attack('Spell Echo',15,'Magic',mechanic='echo'), guard('Arcane Ward','Magic')]),
    dict(id='sporestag', name='Sporestag', type='Physical', maxHp=120, art='Sporestag', moves=[
        attack('Horn Jab',22,'Physical',contact=True), status('Spore Cloud','spores','Spirit'),
        attack('Antler Harvest',18,'Spirit',contact=True,mechanic='harvest'), guard('Chitin Shell','Physical',contact=True)]),
    dict(id='glowmire', name='Glowmire', type='Spirit', maxHp=90, art='Glowmire', moves=[
        attack('Ember Beam',23,'Magic'), attack('Soul Siphon',16,'Spirit',mechanic='drain'),
        heal('Lantern Flare',12), status('Revealing Light','expose','Spirit')]),
    dict(id='bramblebelly', name='Bramblebelly', type='Physical', maxHp=120, art='Sporestag', moves=[
        attack('Bramble Bash',24,'Physical',contact=True), guard('Root Snare','Spirit'),
        attack('Thorn Burst',20,'Spirit'), status('Thorn Coat','thorns','Physical')]),
    dict(id='veyne', name='Veyne', type='Physical', maxHp=100, art='Mage', moves=[
        attack('Steady Shot',22,'Physical'), attack('Runic Arrow',20,'Magic'),
        attack('Piercing Volley',18,'Physical',mechanic='exploit'), status('Mark Prey','mark','Physical')]),
    dict(id='coil', name='Coil', type='Magic', maxHp=100, art='Glowmire', moves=[
        attack('Spark Bolt',23,'Magic'), attack('Coil Lash',20,'Physical',contact=True),
        status('Static Lock','paralyse'), status('Voltage Leak','weaken')]),
    dict(id='bastion', name='Bastion', type='Physical', maxHp=120, art='Mage', moves=[
        guard('Shield Bash','Physical',contact=True), attack('Stone Fist',23,'Physical',contact=True),
        attack('Reprisal',14,'Physical',contact=True,mechanic='reprisal'), attack('Rune Pulse',20,'Magic')]),
    dict(id='vesperfang', name='Vesperfang', type='Magic', maxHp=100, art='Sporestag', moves=[
        attack('Dusk Bolt',22,'Magic'), attack('Night Fang',21,'Spirit',contact=True),
        attack('Dread',18,'Magic',mechanic='dread'), status('Terrify','expose')]),
    dict(id='hushwing', name='Hushwing', type='Spirit', maxHp=90, art='Glowmire', moves=[
        attack('Echo Strike',22,'Spirit'), heal('Soft Wing',10),
        attack('Wing Buffet',20,'Physical',contact=True), status('Disorient','confuse','Spirit')]),
    dict(id='riftclaw', name='Riftclaw', type='Spirit', maxHp=100, art='Sporestag', moves=[
        attack('Rift Slash',24,'Spirit',contact=True), attack('Phase Strike',18,'Spirit',contact=True,mechanic='phase'),
        attack('Reality Tear',20,'Magic'), status('Fracture','expose','Spirit')]),
]
BY_ID = {character['id']: character for character in ROSTER}

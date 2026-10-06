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
# Profiles stay near ten so move power remains readable while roles differ.
# power, focus, armour, ward, recovery
PROFILES = {
    'mage': (8,12,9,11,10), 'sporestag': (11,9,12,9,10),
    'glowmire': (7,11,8,11,10), 'bramblebelly': (11,8,12,9,10),
    'veyne': (12,9,9,9,9), 'coil': (9,12,10,10,8),
    'bastion': (10,8,13,11,8), 'vesperfang': (9,12,9,10,9),
    'hushwing': (8,10,8,12,12), 'riftclaw': (11,11,9,9,8),
}
SIGNATURES = {'mage':[0,2], 'sporestag':[1,2], 'glowmire':[1,2],
              'bramblebelly':[0,3], 'veyne':[2,3], 'coil':[0,2],
              'bastion':[0,2], 'vesperfang':[0,2], 'hushwing':[1,3], 'riftclaw':[0,1]}
ALTERNATIVES = {
    'mage':[status('Sapping Rune','weaken'), attack('Spectral Lance',20,'Spirit')],
    'sporestag':[attack('Chitin Kick',20,'Physical',contact=True), status('Fungal Haze','weaken','Spirit')],
    'glowmire':[attack('Ghost Spark',20,'Spirit'), guard('Lantern Ward','Magic')],
    'bramblebelly':[heal('Second Wind',10), attack('Stone Toss',20,'Physical')],
    'veyne':[status('Disarming Shot','weaken','Physical'), attack('Spirit Arrow',20,'Spirit')],
    'coil':[guard('Magnetic Screen','Magic'), attack('Soul Current',20,'Spirit')],
    'bastion':[heal('Rally',10), status('Crushing Shout','weaken','Physical')],
    'vesperfang':[attack('Shadow Siphon',12,'Spirit',mechanic='drain'), guard('Dusk Mantle','Magic')],
    'hushwing':[status('Unsettling Cry','expose','Spirit'), attack('Moon Spark',20,'Magic')],
    'riftclaw':[guard('Phase Shell','Spirit'), status('Nerve Tear','weaken','Physical')],
}
for character in ROSTER:
    power,focus,armour,ward,recovery=PROFILES[character['id']]
    character['stats']=dict(hp=character['maxHp'],power=power,focus=focus,armour=armour,ward=ward,recovery=recovery)
    character['signatureMoves']=SIGNATURES[character['id']]
    character['movePool']=character['moves']+ALTERNATIVES[character['id']]
BY_ID = {character['id']: character for character in ROSTER}

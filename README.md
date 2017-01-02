# Alchemy Sphere: A Magic-Focused Roguelike

## Introduction

The goal of Alchemy Sphere is to provide a well-calibrated and simple
roguelike world as a background for a rich, complex, and interesting
magic system.

## The Color Magic System

In Alchemy Sphere's magic system, there are two main categories and
several sub-categories.  The two main categories are _magic
generators_ and _magic channelers_.

### Magic Generators

The magic generators are mostly artifacts such as rings, armor, or
runestones that generate a certain color of magic. They normally, once
identified, have the color of their house of magic. The colors (or
houses) of magic are:

* Purple: Magic that has to do with shape-changing and transforming.
* Green: Magic that has to do with monsters and nature.
* White: Magic that has to do with healing and light.
* Black: Magic that has to do with poison and rock.
* Red: Magic that has to do with attack.
* Blue: Magic that has to do with defence.
* Yellow: Magic that has to do with skill-levels and experence points.

A player accrues experience points in each house of magic as he casts
spells in them. Each color of experience points (XP) increase the
likelihood of the spells of the corresponding color of magic
succeeding. When spells fail, they can either have a random effect or
just do nothing. When spells succeed, they do exactly what the
spellbook (or scroll) from which you learned it said. You are always
told wether a spell succeeded or failed.

With each spell, there is an amount of experience points (XP) necissary to
cast it, as well as the amount of "color power" it uses. Each magic
generator only produces a specific amount of "color power", which can
be used to cast a spell. To fully regenerate its color power takes
four turns, but color power can be used partially.

> **Example**: You have a ring that produces 5 purple color power (5P
> CP). You can cast one 5P spell, or a 3P spell and a 2P spell. After
> this, it takes four game turns to cool down the ring and restore its
> full power.


### Magic Channelers

_Magic channelers_, on the other hand, are items, like weapons or
rooms in a dungeon, that have a specific spell or action associated
with them. When in the presence of the right kind of magic, the spell
associated with it will activate.

### Learning, Spellbooks and Scrolls

The player can learn an unlimited number of spells, but it takes one
or more turns to learn a spell. Once a spell is learnt, however, it
may be cast at any time, provided the right color magic generator is
present to power it. If you have less than the required experence
points required to cast it, you have a 100 percent chance minus the
difference.

> **Example**: for a spell that requires 20XP, and you have 18XP, you
> have a 98% chance of success.

It takes the same number of turns as the difference between the
required XP and your XP (or one at the least) to learn a spell.

Each time you successfully cast a certain color of magic, if it
requires more XP than you have, you gain the difference. Thus, you
have to continually seek out new spells to grow as a spellcaster.

Spellbooks normally contain a list of up to five spells that you can
learn, all of the same type of color magic, while scrolls normally
contain only one spell of a much better quality and higher XP. Unlike
spellbooks, once you have learned a scroll's spell, it dissapears
forever.

## The Potion System

The potion system is only slightly superiour to a regular roguelike's,
since there are only two things you can do with a potion: drink it and
mix it with another one. Then new mixed potion does what both potions
would do, including teleportation side effects and so on.

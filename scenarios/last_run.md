# Scenario run (2026-10-23 22:32)

Core Rules 2026-10-09

## combat-damage-assignment

**Q:** I attack a battlefield with one 5 Might unit. My opponent has two 3 Might units defending there. Can I assign 3 damage to one and 2 to the other, or must it be split differently?

- status: **answered** (confidence high, gemini gemini-2.5-flash, 17.05s)
- refined question: In a combat where the attacking player has 5 total Might and the defending player has two 3 Might units, how must the attacking player assign combat damage to the defending units?
- short answer: Yes, you must assign 3 damage to one of your opponent's 3 Might units and the remaining 2 damage to the other 3 Might unit.
- citations: CR 467.2.c, CR 467.2.c.3, CR 467.2.c.4, CR 467, CR 467.2.a, CR 467.2.b, CR 467.2.c.1.a, CR 467.2.c.1
- warnings: none

**Result:** PASS

## ambiguous-respond-to-spell

**Q:** My opponent played a spell targeting my unit. Can I respond with one of my spells to save it?

- status: **needs_clarification** (confidence high, gemini gemini-2.5-flash, 13.81s)
- refined question: If your opponent plays a spell that targets one of your units, can you play one of your spells in response to potentially 'save' that unit?
- short answer: Does your spell have the Reaction keyword?
- citations: none
- warnings: none

**Result:** PASS

## ambiguous-respond-to-spell-clarified

**Q:** My opponent played a spell targeting my unit. Can I respond with one of my spells to save it?

**Clarification:** My spell has [Reaction]. It is my opponent's turn and their spell is still on the chain.

- status: **answered** (confidence high, gemini gemini-2.5-flash, 19.08s)
- refined question: Can a player play a spell with the [Reaction] keyword from their hand to save their unit after an opponent has played a spell targeting that unit, while the opponent's spell is still on the Chain and it is the opponent's turn?
- short answer: Yes, you can play a spell with the [Reaction] keyword from your hand during your opponent's turn while their spell is on the Chain. If your spell moves your unit to a location where it no longer meets the opponent's spell's targeting requirements, the opponent's spell will not affect that unit.
- citations: CR 813.1.c.1, CR 420.2, CR 813.1.b, CR 359.3.e.2, CR 359.3.e.6, S3, CR 359.3.e.9, CR 359.3.a, CR 359.3.c
- warnings: none

**Result:** PASS

## errata-elnuk-herd

**Q:** I played Elnuk Herd from face down. Can its play ability give +3 Might to Elnuk Herd itself?

- status: **answered** (confidence high, gemini gemini-2.5-flash, 12.01s)
- refined question: When Elnuk Herd is played from facedown, can its "When you play me, give a friendly unit +3 [M] this turn" ability target Elnuk Herd itself?
- short answer: Yes, Elnuk Herd's play ability can target Elnuk Herd itself when played from facedown.
- citations: S1, S4, CR 811.1.d.3, CR 811.1.b
- warnings: none

**Result:** PASS

## scoring-twice

**Q:** Can I score the same battlefield twice in one turn if I conquer it, leave, and conquer it again?

- status: **answered** (confidence high, gemini gemini-2.5-flash, 7.4s)
- refined question: Can a player Score the same Battlefield twice in a single turn by Conquering it, then moving their units away, and then Conquering it again?
- short answer: No, a player may only Score a specific Battlefield once per turn, regardless of whether they Conquer or Hold it.
- citations: CR 472, CR 473.1, CR 473.2.a, CR 471, CR 471.1, CR 471.2, CR 488.4, CR 473.2.c
- warnings: none

**Result:** PASS

## gameplay-vs-tournament-banned-card

**Q:** Is Called Shot allowed in my deck?

- status: **needs_clarification** (confidence high, gemini gemini-2.5-flash, 3.51s)
- refined question: Is the card 'Called Shot' legal for inclusion in your deck for a specific game format?
- short answer: Could you please tell me which format you are playing (e.g., Constructed, 2v2 Constructed, or just casual play), and if it's for a sanctioned tournament? Also, if it's a sanctioned Constructed tournament, are you using a preconstructed deck exactly as provided?
- citations: none
- warnings: none

**Result:** PASS

## rotation-2028

**Q:** When Standard rotation starts in 2028, which sets will rotate out?

- status: **answered** (confidence high, gemini gemini-2.5-flash, 13.59s)
- refined question: When Standard rotation begins in 2028, which sets that are currently part of the Standard Constructed format will rotate out?
- short answer: When Standard rotation begins in 2028, all sets released in 2026 and prior years will rotate out of the Standard Constructed format.
- citations: TR 601.3.b, S1, TR 601.3.c.6.a, TR 601.3.c
- warnings: none

**Result:** PASS

## unsupported-next-set

**Q:** What is the next set after Radiance called, and when does it release?

- status: **not_supported** (confidence high, gemini gemini-2.5-flash, 5.16s)
- refined question: What is the name of the set immediately following Radiance, and what is its release date?
- short answer: 
- citations: S1
- warnings: none

**Result:** PASS

## unknown-card

**Q:** If my Shadow Mirage King copies my opponent's legend, do I get its abilities?

- status: **needs_clarification** (confidence high, gemini gemini-2.5-flash, 4.62s)
- refined question: If a game object named 'Shadow Mirage King' copies an opponent's legend, does it gain that legend's abilities?
- short answer: Could you please provide the full card text for 'Shadow Mirage King', including what kind of game object it is and exactly what its copy effect says?
- citations: none
- warnings: none

**Result:** PASS

## hidden-timing

**Q:** Can I hide a card with Hidden face down at a battlefield and then play it on my opponent's turn? What can it choose?

- status: **answered** (confidence high, gemini gemini-2.5-flash, 25.48s)
- refined question: After hiding a card with the [Hidden] keyword facedown at a battlefield you control on your turn, can you play that card on your opponent's subsequent turn, and what are the targeting restrictions for that card or its play effects when played from facedown?
- short answer: Yes, you can play a card with Hidden from facedown on your opponent's turn, and when you do, its targets and play location are generally restricted to the battlefield where it was hidden.
- citations: CR 422.1, CR 422.2, CR 811.1.b, CR 811.6, CR 811.1.c.3, CR 811.1.d.1, CR 811.1.d.1.a, CR 811.1.d.2, CR 811.1.d.3, CR 811.1.d.4, CR 811.1.d.5, CR 811.2, S2, CR 422.2.a, CR 811.1.c.2, CR 420.1, CR 811.1.d
- warnings: none

**Result:** PASS

## direct-rule-lookup

**Q:** What does rule 467.2.c.4 mean in plain English?

- status: **answered** (confidence high, gemini gemini-2.5-flash, 39.25s)
- refined question: What is the meaning and application of Core Rule 467.2.c.4 regarding damage assignment during the Combat Damage Step?
- short answer: During the Combat Damage Step, you cannot assign more damage to a unit than the minimum amount required to deal lethal damage to it, unless it is the last unit remaining to be assigned damage.
- citations: CR 467.2.c.4, CR 467.2.c.3, CR 467.2.c.4.a, CR 467.1, CR 467.2.a, CR 467.2.b, CR 467.2.c, CR 467.2.c.2, CR 467.2.c.1.a, CR 467.2.d, CR 467, CR 467.2.c.1, CR 170.6
- warnings: none

**Result:** PASS

# Scenario run (2026-10-23 21:32)

Core Rules 2026-10-09

## combat-damage-assignment

**Q:** I attack a battlefield with one 5 Might unit. My opponent has two 3 Might units defending there. Can I assign 3 damage to one and 2 to the other, or must it be split differently?

- status: **answered** (confidence high, groq openai/gpt-oss-120b, 14.9s)
- refined question: During the Combat Damage Step, with a single attacking unit of 5 Might and two defending units each with 3 Might, how must the attacker assign its 5 damage among the defenders?
- short answer: You must assign lethal damage (3) to one defender first, then assign the remaining 2 damage to the other defender.
- citations: CR 467.2.c.3, CR 467.2.c.4, CR 467.2.c, CR 467.2.c.1.a, CR 467
- warnings: none

**Result:** PASS

## ambiguous-respond-to-spell

**Q:** My opponent played a spell targeting my unit. Can I respond with one of my spells to save it?

- status: **needs_clarification** (confidence high, groq openai/gpt-oss-120b, 32.57s)
- refined question: When my opponent plays a spell that targets one of my units, can I respond with one of my spells to save that unit?
- short answer: What is the name and full text of the spell you want to play in response, and does it have the Reaction keyword?
- citations: none
- warnings: none

**Result:** PASS

## ambiguous-respond-to-spell-clarified

**Q:** My opponent played a spell targeting my unit. Can I respond with one of my spells to save it?

**Clarification:** My spell has [Reaction]. It is my opponent's turn and their spell is still on the chain.

- status: **answered** (confidence high, groq openai/gpt-oss-120b, 30.26s)
- refined question: During my opponent's turn, after they have played a spell that targets one of my units and the spell is currently on the chain, can I play my own spell that has the [Reaction] keyword to protect that unit?
- short answer: Yes – a spell with the [Reaction] keyword can be played while the opponent’s spell is on the chain, before it resolves.
- citations: CR 813.1.c.1, CR 813.2, CR 313, CR 813, CR 327
- warnings: These rule numbers exist in the official rules but were not among the passages given to the model, so check them yourself: CR 327

**Result:** PASS

## errata-elnuk-herd

**Q:** I played Elnuk Herd from face down. Can its play ability give +3 Might to Elnuk Herd itself?

- status: **answered** (confidence high, groq openai/gpt-oss-120b, 32.47s)
- refined question: When a player hides Elnuk Herd (Hidden) on a battlefield they control, then on a later turn plays it from facedown, can the "When you play me, give a friendly unit +3 [M] this turn" effect target the Elnuk Herd unit itself that is being played?
- short answer: Yes – the play effect may target the Elnuk Herd unit itself, as it is a friendly unit on the battlefield where the card is played.
- citations: CR 811.1.d.3, CR 811.1.b, CR 811.1.c.3, CR 420, S1, CR 811, CR 811.6
- warnings: none

**Result:** PASS

## scoring-twice

**Q:** Can I score the same battlefield twice in one turn if I conquer it, leave, and conquer it again?

- status: **answered** (confidence high, groq openai/gpt-oss-120b, 38.96s)
- refined question: In a 1v1 match, during a player's turn, can that player score the same battlefield twice in the same turn by conquering it, moving a unit off it, and then conquering it again?
- short answer: No – a battlefield can be scored only once per turn, so you cannot score it twice by conquering, leaving, and reconquering.
- citations: CR 471.1, CR 472, CR 471
- warnings: none

**Result:** PASS

## gameplay-vs-tournament-banned-card

**Q:** Is Called Shot allowed in my deck?

- status: **needs_clarification** (confidence high, groq openai/gpt-oss-120b, 14.33s)
- refined question: Is the card Called Shot permitted to be included in the player's deck for the format they intend to play?
- short answer: Which format are you planning to play with this deck?
- citations: none
- warnings: none

**Result:** PASS

## unsupported-2028-rotation

**Q:** When Standard rotation starts in 2028, which sets will rotate out?

- status: **not_supported** (confidence high, groq openai/gpt-oss-120b, 1.17s)
- refined question: When Standard rotation starts in 2028, which sets will rotate out?
- short answer: 
- citations: S1
- warnings: none

**Result:** PASS

## unknown-card

**Q:** If my Shadow Mirage King copies my opponent's legend, do I get its abilities?

- status: **not_supported** (confidence high, groq openai/gpt-oss-120b, 29.51s)
- refined question: If my Shadow Mirage King copies my opponent's legend, do I get its abilities?
- short answer: 
- citations: none
- warnings: none

**Result:** PASS

## hidden-timing

**Q:** Can I hide a card with Hidden face down at a battlefield and then play it on my opponent's turn? What can it choose?

- status: **answered** (confidence high, groq openai/gpt-oss-120b, 15.52s)
- refined question: If I hide a card that has the Hidden keyword face‑down at one of my battlefields, can I later play that hidden card during my opponent's turn, and what restrictions apply to where it can be played and what it can target?
- short answer: Yes—you may play the hidden card on your opponent’s turn because it gains Reaction after being hidden, and you must play it to the battlefield it was hidden on, with any targets limited to that battlefield unless the card’s text says otherwise.
- citations: CR 811.1.c.2, CR 811.6, CR 811.1.c.3, CR 811.1.d.1, CR 811.1.d.5, CR 422, CR 811.1.d.2, CR 811
- warnings: none

**Result:** PASS

## direct-rule-lookup

**Q:** What does rule 467.2.c.4 mean in plain English?

- status: **answered** (confidence high, groq openai/gpt-oss-120b, 31.46s)
- refined question: What is the plain‑English meaning of Core Rule 467.2.c.4 (and its sub‑clause 467.2.c.4.a) that governs how a player must assign combat damage when assigning more damage than the minimum lethal amount is possible?
- short answer: When assigning combat damage, you must assign the smallest amount of damage that will make a unit lethal; you may only assign extra damage to a unit if you have no other legal targets left.
- citations: CR 467.2.a, CR 467.2.b, CR 467.2.c.3, CR 467.2.c.4, CR 467.2.c.4.a, CR 467.2.c.1.a, CR 467
- warnings: none

**Result:** PASS

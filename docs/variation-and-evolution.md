# Variation and Evolution

This document explains how solutions change inside the genetic optimizer and why those changes make sense for the 2D packing task.

## Representation Reminder

A chromosome contains only real items.
There are no coordinates and no virtual blocks in the genome.

The optimizer changes only:

- item order
- rotation flags

That is important because the decoder remains the only place where geometry is constructed.

## Parent Selection

Parents are chosen with tournament selection.
A small random subset of the population is sampled, and the best individual in that subset becomes the parent.

Why it fits this project:

- simple and stable
- no fitness normalization needed
- works well with lexicographic comparison

## Inheritance and Crossover

Inheritance is handled by order crossover.
This is the right kind of crossover for permutation-based chromosomes.

### What it preserves

- every real item remains present exactly once
- no duplicates appear
- no repair by item set is needed afterward

### Task-level meaning

This operator mixes two packing strategies.
Part of the item order is kept from one parent, and the rest is completed from the other parent.

In practice, this lets the algorithm combine:

- one parent that places large blocks well
- another parent that finishes the container better with smaller items

## Rotation Inheritance

Rotation flags are inherited together with the item source.
If an item comes from a specific parent segment, its rotation flag is taken from that same parent.

This keeps orientation decisions tied to the order decisions that produced them.

## Mutations

Mutations are the main source of local exploration.
They do not create or remove items.
They only rearrange real items already present in the chromosome.

### Swap Mutation

Two positions are swapped.

Task-level meaning:

- quickly changes which item gets decoded earlier
- useful when two items compete for the same strategic placement area

### Insert Mutation

One item is removed from position `i` and inserted into position `j`.

Task-level meaning:

- shifts priority without fully scrambling the chromosome
- useful when one large block should move much earlier or later in the sequence

### Inversion Mutation

A whole segment is reversed.

Task-level meaning:

- restructures a local subsequence of packing decisions
- useful when a whole region of the chromosome behaves badly together

### Rotation Flip Mutation

One or more rotatable items have their orientation flipped.

Task-level meaning:

- changes how an item competes for narrow or tall empty spaces
- especially useful near holes or overflow conflicts

## Directed Mutation Near Empty Regions

Mutation is no longer fully blind.
The optimizer detects items that border empty regions.
Overflow items are also treated as gap-related candidates.

Those items are targeted more often by mutations.

Why this is useful for the task:

- if a hole exists, nearby items are the most likely cause
- if an item overflows, its neighbors and its own position are natural repair targets
- the search spends more effort where the packing is visibly imperfect

This keeps the algorithm close to the geometry of the problem without putting geometry directly into the chromosome.

## Elitism

A small part of the best population is copied unchanged to the next generation.

Why it matters:

- strong solutions are not lost
- progress is monotonic at the best-solution level
- the algorithm does not need to rediscover the same top individual repeatedly

## Duplicate Control

The optimizer tracks exact duplicate chromosomes.
If a new child is identical to one already accepted for the generation, it tries to mutate again before giving up.

Why it matters:

- avoids wasting population slots on the same search point
- increases effective exploration

## Immigrants

Immigrants are fresh random chromosomes injected after stagnation.
They are not derived from the current parent pool.

Task-level meaning:

- useful when the population converges to one layout style
- reintroduces alternative large-block orders and orientation patterns
- helps escape local structure traps created by a specific packing arrangement

## Why Large Blocks Are Encouraged Earlier

The current fitness keeps `total_value` as the main objective, but adds a structural secondary score that rewards successful large items placed earlier.

Why this matches the task:

- large rectangles are harder to place later, after the container becomes fragmented
- small rectangles are better suited for compensating irregular leftover regions
- this makes the search closer to practical packing intuition without forcing a rigid rule

## Why Virtual Blocks Are Not Mutated

Virtual blocks are decoder artifacts, not genes.
They exist only to help geometry interpretation and visualization.

Keeping them out of the genome has two advantages:

- the search remains focused on real decisions
- crossover and mutation remain stable and interpretable

## Summary

The optimizer changes chromosomes in four ways that matter most to the packing task:

- inheritance combines useful order/orientation fragments from parents
- mutation repairs local ordering and orientation mistakes
- directed mutation focuses on areas near holes and overflow
- immigrants reintroduce diversity after stagnation

Together, these mechanisms let the search balance structure, diversity, and local repair pressure.

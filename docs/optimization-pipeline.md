# Optimization Pipeline

This document describes the main optimization flow from task loading to the final result shown in the UI.

## 1. Input Task

The process starts with a `ProblemInstance`.
A task contains:

- one rectangular `Container`
- a tuple of rectangular `Item` objects

Each item has:

- `item_id`
- `width`
- `height`
- `can_rotate`

The runtime value rule is fixed:

- `value = width * height`

## 2. Search Representation

The genetic algorithm does not optimize coordinates directly.
It optimizes a compact chromosome:

```python
Chromosome(
    order=("A", "B", "C"),
    rotations=(False, True, False),
)
```

### Meaning

- `order`
  The order in which real items are offered to the decoder.
- `rotations`
  Rotation flags aligned with `order`.

### Important constraints

- each real item appears exactly once
- virtual blocks are not part of the chromosome
- non-rotatable items are normalized to `False`

## 3. Sequence Conversion

Before geometry starts, the chromosome is converted into a `SequenceSolution`.
That is a simple sequence of `Gene(item_id, rotated)` objects.

This conversion separates genetic representation from geometry logic.

## 4. Decoding

The decoder is the first geometric stage.
It receives:

- `ProblemInstance`
- `SequenceSolution`

and produces:

- `DecodedLayout`

### Decoder behavior

The current decoder is a left-bottom decoder.
For each gene it:

1. computes the actual item orientation
2. retrieves current candidate points
3. checks candidate points in `(y, x)` order
4. places the item at the first non-overlapping point
5. allows overflow placements to remain in the layout
6. optionally creates virtual blocks according to the selected void policy

### Decoder output

`DecodedLayout` contains:

- `placements`
  Final placed rectangles, including virtual and overflow placements
- `steps`
  Detailed decode trace for inspection in the UI
- `used_solution_order`
  The processed gene order

## 5. Fitness Evaluation

The decoder does not score anything.
Scoring is handled by `FitnessEvaluator`.

It receives:

- `ProblemInstance`
- `DecodedLayout`

and produces:

- `FitnessBreakdown`

### What is counted

- `total_value`
  Sum of values for real items fully inside the container
- `valid_items_count`
  Count of real items fully inside the container
- `overflow_items_count`
  Count of real items not fully inside the container
- `virtual_blocks_count`
  Count of virtual blocks
- `used_area_inside`
  Container area occupied by valid real placements
- `fill_ratio`
  `used_area_inside / container_area`
- `large_first_score`
  Secondary structural score that prefers solutions where larger valid items appear earlier in successful packing order

### Main comparison rule

Selection remains value-first.
When values tie, the algorithm prefers:

1. larger `large_first_score`
2. more valid items
3. more used area inside the container
4. fewer overflow items

## 6. Individual Construction

A decoded and scored chromosome becomes an `Individual`.
An individual stores:

- chromosome
- fitness breakdown
- decoded layout
- origin type
- optional parent ids

This object is the unit used by selection, history snapshots, and UI inspection.

## 7. Initial Population

The initial population is mixed.
It is built from two sources:

- random chromosomes
- heuristic chromosomes based on deterministic sort orders

The goal is to combine diversity with sensible starting points.

## 8. Evolution Loop

For each generation, the GA performs the following stages.

### Selection

Parents are chosen by tournament selection.
The best individual by fitness key wins the tournament.

### Recombination

Order is inherited with order crossover.
Rotation flags follow the source parent of each copied item.

### Mutation

The chromosome may receive:

- one order mutation
- one rotation mutation

Mutations are not purely random anymore.
If the parent layout has empty regions or overflow placements, neighboring items are targeted more often.
This increases search effort around local packing defects.

### Deduplication

Exact duplicates are detected by chromosome signature.
The algorithm tries additional mutation first and only falls back when needed.

### Elitism

Top individuals are copied to the next generation without re-decoding.
This preserves the best solutions and also saves runtime.

### Optional immigrants

If stagnation immigrants are enabled and the run stalls, a fraction of the population is replaced with new random chromosomes.

## 9. Stopping Conditions

The GA stops when any of the following becomes true:

- `max_generations` reached
- `stagnation_limit` reached
- `max_time_seconds` reached
- `fill_ratio == 1`

The last condition means the container is fully filled, so there is no reason to continue the search.

## 10. Baseline Comparison

If enabled, the application can run an exhaustive baseline after GA.
This is only intended for small tasks.

The exhaustive baseline enumerates:

- every item order
- every allowed rotation combination

and evaluates them through the same decoder and fitness pipeline.

This gives a direct comparison between:

- GA best value and duration
- exhaustive best value and duration
- exhaustive search space size and status

## 11. History and UI Mapping

The final GA run produces a `GAResult`.
It contains:

- best individual
- final population
- run history
- config
- duration

The UI then maps that result into:

- generation table rows
- individual table rows
- scene rendering
- decode-step inspection
- charts
- optional comparison against population study and exhaustive baseline

## 12. Summary of Representations

The same solution passes through several representations.
Each exists for a specific reason.

- `ProblemInstance`
  Static input task
- `Chromosome`
  Search-space representation for GA operators
- `SequenceSolution`
  Decoder-ready ordered genes
- `DecodedLayout`
  Geometric result of decoding
- `FitnessBreakdown`
  Numeric evaluation of the decoded layout
- `Individual`
  GA entity combining chromosome, geometry, and score
- `GAResult`
  Final run output for history, exports, and UI

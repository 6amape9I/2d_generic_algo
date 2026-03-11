# 2D Knapsack

Educational Python project for constrained 0/1 two-dimensional knapsack.

## Problem

- One rectangular container.
- Finite set of rectangular items.
- Optional 90-degree rotation for each item.
- No overlaps.
- Goal: maximize total value.

## Current representation

A solution stores only:

- order of item ids;
- rotation flag for each item.

Coordinates are produced by the decoder.

## Decoder

The decoder applies left-bottom candidate placement:

- iterates genes in sequence order;
- checks candidate points in bottom-left order (`y`, then `x`);
- places item at first non-overlapping point;
- overflow placements are allowed and preserved in layout.

Virtual blocks can be enabled via policy. They are geometry-only blocks with:

- `item_id=None`
- `value=0`
- `is_virtual=True`

## Fitness policy

Fitness is strict:

- virtual blocks always contribute `0`;
- any real item that is not fully inside the container contributes `0`.

## TXT format

Example:

```txt
NAME demo_small
CONTAINER 10 6

ITEMS
# id width height value can_rotate
A 3 2 8 1
B 4 3 12 1
C 5 2 7 0
```

## Run tests

```bash
python -m pytest
```

## Run UI

```bash
python -m knapsack2d.ui.app
```

Main UI flow:

1. Load `.txt` task.
2. Set GA parameters (population, generations, policies, history mode, seed).
3. Run optimization.
4. Inspect generations and individuals.
5. Use playback slider (`Prev/Next/Play/Pause`).
6. Inspect layout, genes, placements, decode steps.
7. Export:
   - history JSON,
   - selected layout PNG,
   - best report JSON/TXT.

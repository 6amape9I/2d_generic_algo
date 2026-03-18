# UI Guide

The application is built around one main window and one statistics window.
The main window is optimized for running the solver, browsing generations, and inspecting layouts.

## Top Bar

### `Settings`
Opens the configuration dialog.
This is where the genetic algorithm, history settings, population study, and exhaustive baseline are configured.

### `Load Task`
Loads a task from a `.txt` file.
The file defines container size and item list.

### `Run`
Starts the genetic algorithm with the current settings.
If `Population Study` is enabled, the task is solved multiple times with different population sizes.
If `Baseline` is enabled, exhaustive search is also launched after GA, but only on sufficiently small tasks.

### `Stop`
Requests a graceful stop.
The current generation is allowed to finish cleanly.

### `Statistics`
Opens the statistics window.
The window contains generation charts, population study charts, and GA vs exhaustive comparison.

### `Export History JSON`
Exports the current run history, including generation summaries and any available study/baseline data.

### `Export Layout PNG`
Exports the currently selected individual layout as an image.

### `Export Best Report`
Exports a compact report for the best GA solution.

## Settings Dialog

The dialog is divided into tabs.

### `GA`
Controls the main GA run.

- `Population`
  Population size for a normal GA run.
- `Generations`
  Maximum number of generations.
- `Stagnation`
  Number of generations without improvement before stopping.
- `Tournament`
  Tournament size for parent selection.
- `Seed`
  Random seed for deterministic runs.
- `Max Time`
  Optional time limit for the GA.
- `P Crossover`
  Probability of crossover.
- `P Order Mutation`
  Probability of one order mutation.
- `P Rotation Mutation`
  Probability of rotation mutation.
- `Random Init Ratio`
  Fraction of random individuals in the initial population.

### `History`
Controls what is stored and how timeline playback behaves.

- `History Mode`
  `best_only`, `top_k`, or `full_population`.
- `History Top K`
  Number of individuals stored per generation in `top_k` mode.
- `Play Interval`
  Delay between timeline steps during playback.

### `Policies`
Controls optional solver policies.

- `Void Policy`
  Controls whether decoder-created virtual blocks are disabled or enabled.
- `Immigrants`
  Enables stagnation immigrants.
- `Immigrant Fraction`
  Fraction of the population replaced by immigrants on stagnation.

### `Population Study`
Runs the same task on five different population sizes.
The best GA result among those runs becomes the primary result shown in the main window.
The full comparison appears in `Statistics`.

- `Enable Study`
  Turns the study mode on or off.
- `Population #1 ... Population #5`
  Five population sizes to compare.

### `Baseline`
Controls exhaustive search.

- `Enable Baseline`
  Runs exhaustive search after GA.
- `Max Items`
  Safety limit. If the task has more items than this number, exhaustive search is skipped.
- `Max Time`
  Optional time limit for exhaustive search.

## Layout Block

The layout block is the main visual area of the application.
It is placed in the left part of the main window.
The layout itself is centered inside the view for readability.

### `Fit`
Fits the full container into the current viewport.

### `Reset Zoom`
Resets the zoom transform.

### `Pan mode`
Switches the view into drag mode.

### `Show virtual`
Shows or hides decoder-created virtual blocks.

### `Show overflow`
Shows or hides overflow placements.

### `Show labels`
Shows or hides item labels drawn inside blocks.

### `Show candidate points`
Shows or hides candidate points for the currently selected decode step.

### Legend
Explains color mapping.

- blue: valid placed items
- red dashed: overflow placements with zero value
- gray: virtual blocks

## Generation Timeline

### `Prev`
Moves to the previous generation.

### `Next`
Moves to the next generation.

### `Play`
Starts timeline playback.

### `Pause`
Stops timeline playback.

### Generation Slider
Jumps directly to a generation.

### Timeline Label
Shows the current generation index and total number of saved generations.

## Left and Right Panels

The right side of the main window contains inspection tools.

### `Generations` table
Shows one row per generation with aggregate metrics.
Selecting a generation updates the individuals list.

### `Individuals` table
Shows stored individuals for the selected generation.
Selecting an individual updates the layout, details, genes, placements, and decode steps.

### `Details` tab
Shows the main metrics of the selected individual.

### `Genes` tab
Shows chromosome order and rotation flags.

### `Placements` tab
Shows decoded placements.
Selecting a row highlights the placement on the scene.

### `Decode Steps` tab
Shows the step-by-step decoder trace.
Selecting a step highlights the corresponding placement and, when enabled, candidate points.

## Statistics Window

The statistics window is split into tabs.

### `Run History`
Generation charts for:

- best value
- average value
- diversity
- best fill ratio
- best overflow count

### `Population Study`
Charts comparing best value and duration for the five configured population sizes.

### `Baseline`
Compares GA against exhaustive search.
This tab shows:

- GA best value vs exhaustive best value
- GA duration vs exhaustive duration
- exhaustive status and the number of evaluated candidate solutions

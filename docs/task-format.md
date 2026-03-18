# Task Format

Tasks are loaded from plain text files.

## Structure

```txt
NAME <task_name>
CONTAINER <width> <height>

ITEMS
# id width height area_value can_rotate
A 3 2 6 1
B 4 3 12 1
C 5 2 10 0
```

## Sections

### `NAME`
Task name shown in the UI.

### `CONTAINER`
Container width and height.
Both values must be positive integers.

### `ITEMS`
List of items.
Each line describes one rectangle.

Supported line formats:

```txt
<id> <width> <height> <can_rotate>
<id> <width> <height> <value> <can_rotate>
```

## Notes

- empty lines are ignored
- lines starting with `#` are comments
- item ids must be unique
- `can_rotate` must be `0` or `1`
- width and height must be positive integers

## Value Handling

The loader still accepts a `value` column for compatibility.
However, runtime logic overrides item value with:

- `width * height`

So the actual optimization value is always equal to area.

## Example Files

See:

- `data/tasks/demo_small.txt`
- `data/tasks/demo_medium.txt`
- `data/tasks/demo_large.txt`
- `data/tasks/demo_extreme.txt`

"""Conway's Life as a discrete mathematical model, not a physical law."""

from collections.abc import Sequence


def game_of_life(grid: Sequence[Sequence[int]], *, periodic: bool = False) -> list[list[int]]:
    """One B3/S23 update using Moore neighbors on a rectangular binary grid.

    Nonperiodic boundaries have fixed dead exterior. For periodic grids each
    offset counts separately, so dimensions below 3 are rejected to avoid
    assigning the same neighbor to multiple offsets.
    """
    rows = len(grid)
    if not rows or not grid[0]:
        raise ValueError("grid must be nonempty")
    cols = len(grid[0])
    if any(len(row) != cols or any(value not in (0, 1) for value in row) for row in grid):
        raise ValueError("grid must be rectangular and binary")
    if periodic and min(rows, cols) < 3:
        raise ValueError("periodic grids need at least 3 rows and columns")
    output = [[0] * cols for _ in range(rows)]
    for row in range(rows):
        for col in range(cols):
            neighbors = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == dx == 0:
                        continue
                    y, x = row + dy, col + dx
                    if periodic:
                        neighbors += grid[y % rows][x % cols]
                    elif 0 <= y < rows and 0 <= x < cols:
                        neighbors += grid[y][x]
            output[row][col] = int(neighbors == 3 or (grid[row][col] == 1 and neighbors == 2))
    return output

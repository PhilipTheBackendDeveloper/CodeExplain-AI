"""
Sample Code 2 — A data processing pipeline.

Demonstrates: recursion, generators, complex loops, nested functions,
type annotations, multiple classes. Good for complexity analysis testing.
"""

from typing import Generator, Any, Callable


class DataPipeline:
    """
    A configurable data processing pipeline.

    Processors are applied in sequence to each record.
    """

    def __init__(self, name: str):
        self.name = name
        self._processors: list[Callable] = []
        self._filters: list[Callable] = []

    def add_processor(self, func: Callable) -> "DataPipeline":
        """Add a data transformation function to the pipeline."""
        self._processors.append(func)
        return self  # Fluent interface

    def add_filter(self, func: Callable) -> "DataPipeline":
        """Add a filter predicate. Records failing filter are dropped."""
        self._filters.append(func)
        return self

    def run(self, data: list[Any]) -> list[Any]:
        """Run the pipeline over a dataset and return results."""
        results = []
        for record in data:
            # Apply all filters
            passes = True
            for f in self._filters:
                if not f(record):
                    passes = False
                    break
            if not passes:
                continue

            # Apply all processors in order
            processed = record
            for processor in self._processors:
                try:
                    processed = processor(processed)
                except Exception as e:
                    processed = None
                    break

            if processed is not None:
                results.append(processed)
        return results


def flatten(data) -> Generator:
    """Recursively flatten nested lists into a single generator."""
    for item in data:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


def merge_sort(arr: list) -> list:
    """Sort a list using the merge sort algorithm (recursive)."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list, right: list) -> list:
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def compute_statistics(data: list[float]) -> dict:
    """
    Compute basic statistics for a list of numbers.

    Returns mean, median, min, max, and standard deviation.
    """
    if not data:
        return {}

    n = len(data)
    mean = sum(data) / n

    sorted_data = merge_sort(data[:])
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        median = sorted_data[n // 2]

    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = variance ** 0.5

    return {
        "count": n,
        "mean": round(mean, 4),
        "median": median,
        "min": min(data),
        "max": max(data),
        "std_dev": round(std_dev, 4),
        "range": max(data) - min(data),
    }


def group_by(data: list[dict], key: str) -> dict[str, list[dict]]:
    """Group a list of dicts by a specific key."""
    groups: dict[str, list] = {}
    for item in data:
        value = str(item.get(key, "unknown"))
        if value not in groups:
            groups[value] = []
        groups[value].append(item)
    return groups


class CSVProcessor:
    """Parses and processes simple CSV-formatted data."""

    def __init__(self, delimiter: str = ",", has_header: bool = True):
        self.delimiter = delimiter
        self.has_header = has_header
        self.headers: list[str] = []

    def parse(self, raw: str) -> list[dict]:
        """Parse raw CSV text into a list of dicts."""
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        if not lines:
            return []

        if self.has_header:
            self.headers = [h.strip() for h in lines[0].split(self.delimiter)]
            data_lines = lines[1:]
        else:
            data_lines = lines
            self.headers = [f"col_{i}" for i in range(len(lines[0].split(self.delimiter)))]

        records = []
        for line in data_lines:
            values = [v.strip() for v in line.split(self.delimiter)]
            if len(values) == len(self.headers):
                records.append(dict(zip(self.headers, values)))
        return records

    def to_csv(self, records: list[dict]) -> str:
        """Serialize a list of dicts back to CSV format."""
        if not records:
            return ""
        headers = list(records[0].keys())
        lines = [self.delimiter.join(headers)]
        for record in records:
            row = [str(record.get(h, "")) for h in headers]
            lines.append(self.delimiter.join(row))
        return "\n".join(lines)


if __name__ == "__main__":
    # Demo: build and run a pipeline
    pipeline = (
        DataPipeline("demo")
        .add_filter(lambda x: x is not None)
        .add_processor(str.strip)
        .add_processor(str.lower)
    )

    data = ["  Hello  ", None, "  WORLD  ", "  Python  "]
    result = pipeline.run(data)
    print("Pipeline:", result)

    # Demo: statistics
    numbers = [4.2, 7.1, 2.8, 9.4, 1.5, 6.3, 3.7]
    stats = compute_statistics(numbers)
    print("Stats:", stats)

    # Demo: flatten
    nested = [[1, [2, 3]], [4, [5, [6]]]]
    print("Flatten:", list(flatten(nested)))

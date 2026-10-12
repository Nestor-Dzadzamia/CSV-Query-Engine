# csvquery

A small Python library for querying CSV files. You give it one file or a folder of files with the same columns, chain some operations, and save the result. It reads one row at a time, so the file can be bigger than your RAM.

```python
from csvquery import CSVData

result = (
    CSVData("data/")
    .filter("price > 500 AND brand == 'apple'")
    .select("brand", "price", "event_type")
    .sort("price", descending=True)
    .limit(100)
)
result.save("output/result.csv")
```

## Installation

Python 3.12 or newer.

```bash
git clone https://github.com/Nestor-Dzadzamia/CSV-Query-Engine.git
cd CSV-Query-Engine
uv sync
```

Or `pip install -e .` if you don't use uv.

One thing to know: schema validation runs in separate processes. On macOS and Windows this means your script has to use the standard main guard, otherwise Python complains about spawning processes on import.

```python
if __name__ == "__main__":
    data = CSVData("data/")
```

## Usage

`CSVData(path)` takes either a single `.csv` file or a directory. If it's a directory, every `.csv` in it is checked against the first one and they're treated as one dataset.

Creating a `CSVData` validates the schema right away. After that, each operation you chain just gets added to a list. Nothing actually reads the file until you call `save()` or loop over the object.

```python
data = CSVData("data/")

data.filter("price > 100").select("brand", "price").limit(10).save("out.csv")

for row in CSVData("data/").filter("brand == 'samsung'").limit(5):
    print(row)

for row in CSVData("data/").filter("price > 500").count():
    print(row)  # {'COUNT(*)': '2384117'}

for row in CSVData("data/").group_by("brand", "price", "avg"):
    print(row)  # {'brand': 'apple', 'AVG(price)': '891.14'}
```

It also works as a context manager. The queued operations get cleared when the block ends.

```python
with CSVData("data/") as data:
    data.filter("price > 100").save("out.csv")
```

### Configuration

```python
from csvquery import CSVData
from csvquery.config import PipelineConfig

config = PipelineConfig(chunk_size=500_000, encoding="utf-8", max_workers=4)
data = CSVData("data/", config=config)
```

| Field | Default | What it controls |
|---|---|---|
| `chunk_size` | `1_000_000` | Rows per chunk during validation |
| `encoding` | `"utf-8-sig"` | File encoding. The `-sig` variant strips a BOM if there is one |
| `max_workers` | CPU count | How many files get validated in parallel |

### Logging

The library logs how long schema validation and query execution took, and their peak memory, through the standard `logging` module. It doesn't set up logging itself. Turn it on in your script if you want to see it:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Supported operations

| Operation | What it does | Memory |
|---|---|---|
| `filter(expression)` | Keep rows matching an expression | one row at a time |
| `select(*columns)` | Keep only the named columns | one row at a time |
| `limit(n)` | Keep the first `n` rows and stop reading | one row at a time |
| `sort(*columns, descending=False)` | Order rows. Nulls go last | holds every row that reaches it |
| `count(column="*")` | One row with the count. `COUNT(*)` counts everything, `COUNT(col)` skips nulls | one counter |
| `group_by(group_col, agg_col, agg_func)` | One row per group. `agg_func` is `sum`, `count`, `avg`, `min`, or `max` | one accumulator per group |
| `save(path)` | Run the query and write the result | one row at a time |

Operations run in the order you chain them. That matters: `filter` then `sort` sorts only the matching rows, while `sort` then `filter` sorts the whole file first.

Column names are checked when you chain the operation, not when the query runs. `select("nope")` raises immediately.

## Query expressions

```
expression  := or_expr
or_expr     := and_expr ( OR and_expr )*
and_expr    := primary ( AND primary )*
primary     := "(" expression ")" | comparison
comparison  := COLUMN OPERATOR VALUE
OPERATOR    := ">=" | "<=" | "==" | "!=" | ">" | "<"
VALUE       := NUMBER | 'STRING' | true | false
```

- `AND` binds tighter than `OR`. Use parentheses to change that.
- Keywords are case-insensitive, so `and` and `AND` are the same.
- Strings go in single or double quotes: `brand == 'apple'`.
- The value is cast to the column's type before comparing. Writing `price > 'abc'` on a numeric column raises `ExpressionError` when you chain it, not during the query.
- A null cell never matches anything.

```python
.filter("price > 500")
.filter("brand == 'apple' AND price > 1000")
.filter("(brand == 'apple' OR brand == 'samsung') AND event_type == 'purchase'")
```

Under the hood the expression is tokenized, parsed into a small tree, and compiled into a function. That function captures the column index, the operator, and the already-cast literal, so the per-row work is just a lookup and a comparison.

## How it works

**The pipeline is lazy.** Each builder method appends an operation and returns `self`. When you call `save()` or iterate, the reader opens the files and yields rows one by one. Every operation is a generator that takes a stream of rows and gives back a stream of rows. A row goes through the whole chain before the next one gets read. So memory stays flat no matter how big the file is, for everything except `sort`.

**Validation happens first.** When you create a `CSVData`, it looks at the first non-null value in each column to decide its type, then checks every row of every file against that. Column names and count have to match, numeric columns have to parse, boolean columns have to be `true` or `false`. If something's off you get an error with the file, row, and column before any query runs. Multiple files are validated in parallel.

## Performance

Tested on the [eCommerce behavior dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store) from Kaggle. Two files, 14 GB, about 110 million rows.

Schema validation, checking every row:

| Version | Time |
|---|---|
| Pure Python, checked every cell, used a regex for inf/nan | ~13 min |
| Skip string columns, replace the regex with a set lookup | ~3 min |
| pandas chunked read on numeric columns only | ~1 min |
| Plus one process per file | ~30 s |

The slow part turned out to be Python doing per-cell work, not disk reads. Bigger read buffers changed nothing. pandas got it under a minute because its C parser never touches the string columns and casts numbers without a Python loop.

### A full run

This is `examples/target.py` against the whole 14 GB dataset: select six columns, filter on brand and price, write every matching row to a file.

```python
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    data = CSVData("data/")
    result = (
        data.select("event_time", "event_type", "brand", "price", "user_id", "user_session")
        .filter("(brand == 'samsung') and (price < 200)")
    )
    result.save("output.csv")
```

```
2026-09-19 19:14:13,411 - INFO - schema validation took 31.226 seconds
2026-09-19 19:14:13,412 - INFO - schema validation peak memory usage 0.5 MB
2026-09-19 19:30:18,292 - INFO - query execution took 964.864 seconds
2026-09-19 19:30:18,298 - INFO - query execution peak memory usage 8.2 MB
```

| Stage | Time | Peak memory |
|---|---|---|
| Schema validation, both files | 31 s | 0.5 MB |
| Query: read 110M rows, filter, write matches | 16 min | 8.2 MB |

The query reads every row of 14 GB, runs the compiled filter on each, and streams the matches to disk. Peak memory is 8.2 MB for the whole thing. That's the point of the design: the file size doesn't change how much RAM the query needs.

Validation memory is measured in the parent process. The per-file work happens in worker processes, which `tracemalloc` doesn't see.

## Design decisions

- **Builders return `self`.** A `CSVData` is a mutable query object. Simpler to reason about. The cost is that you can't take one base dataset and branch two queries off it.
- **stdlib `csv` for reading.** We wrote a parser by hand first and checked it against `csv` on the awkward cases (quoted commas, embedded newlines, escaped quotes). Then measured: `csv.reader` was 6.7 times faster. Kept the stdlib one.
- **pandas only for validation.** Reading and querying are pure Python because being lazy matters more than being fast there. Validation is a full scan where speed is all that matters, and pandas with `chunksize` keeps memory bounded.
- **Type is decided by the first non-null value.** No widening. A column is one type plus nulls. `10` in a float column is fine since `float("10")` works. `10.5` in an integer column is not. Text in a numeric column is not.
- **Row shape is strict.** A row with more or fewer cells than the header fails validation. We don't pad it.
- **Nulls are `""`, `NA`, `N/A`, `NULL`, `null`.** Aggregations skip them. Filters never match them.
- **`sort` is in memory.** It holds every row that reaches it. Filter first if you can.
- **One aggregate per `group_by`.** One group column, one value column, one function.

## Errors

Everything the library raises inherits from `CSVQueryError`, so you can catch that one if you don't care which.

| Class | When |
|---|---|
| `SourceError` | Path doesn't exist, isn't a CSV, or the file or directory is empty |
| `SchemaError` | Files don't agree on columns, or a cell doesn't fit its column type |
| `ColumnError` | An operation used a column name that doesn't exist |
| `ExpressionError` | A filter expression couldn't be tokenized, parsed, or compiled |
| `OperationError` | An operation got arguments it can't work with |

```python
from csvquery import CSVData, CSVQueryError

try:
    CSVData("data/").filter("price >").save("out.csv")
except CSVQueryError as error:
    print(error)  # expected a value after '>' at position 7
```

## Known limitations

- `sort` holds all rows that reach it. Sorting the whole dataset without a filter first would need an external merge sort, which isn't implemented.
- You can't reference columns that `group_by` or `count` create (like `AVG(price)` or `COUNT(*)`) in later operations. Those still validate against the original schema.
- Type inference uses the first non-null value. If the first row is corrupt, the schema is wrong and validation fails on the first good row instead.
- Boolean columns only accept `true` and `false`, in any case.
- `group_by` does one aggregate at a time.

## Running tests

```bash
uv run pytest
uv run mypy src/
```

## Project structure

```
src/csvquery/
├── csv_data.py          CSVData, the public API
├── config.py            PipelineConfig
├── expression/          tokenizer, parser, compiler
├── operations/          filter, select, sort, limit, count, group_by
├── schema/              file resolution, type inference, validation
├── io_handlers/         streaming reader, writer
└── util/                timed and memory_usage decorators, errors
```

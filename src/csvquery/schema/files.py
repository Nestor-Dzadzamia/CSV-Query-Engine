from pathlib import Path


def retrieve_validate_files(path: str) -> list[Path]:
    target = Path(path)

    if not target.exists():
        raise FileNotFoundError(f"The path {path!r} does not exist")

    if target.is_file():
        if target.suffix != ".csv":
            raise ValueError(f"not a CSV file: {path!r}")
        return [target]

    files = []

    for file in target.iterdir():
        if file.suffix != ".csv":
            continue
        files.append(file)

    files = sorted(files, key=lambda f: f.name) # aq vsortav, filesystemma sheileba aradeterministulad waikitxos

    if not files:
        raise ValueError(f"the directory {path!r} contains no .csv files")
    return files

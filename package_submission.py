"""Create submission.zip with only output/ after final QA passes."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from src.config import BASE_DIR, OUTPUT_DIR
from validate_outputs import main as validate_outputs


def main() -> int:
    if validate_outputs() != 0:
        return 1
    archive = BASE_DIR / "submission.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
        for file_path in sorted(OUTPUT_DIR.glob("EC_*.json")):
            zip_file.write(file_path, Path("output") / file_path.name)
    print(f"Created {archive.name} with 50 output files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

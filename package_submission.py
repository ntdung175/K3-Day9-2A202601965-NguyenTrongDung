"""Package only output/ after QA has passed."""
from zipfile import ZipFile, ZIP_DEFLATED
from src.config import BASE_DIR, OUTPUT_DIR
from validate_outputs import main as validate
def main():
    if validate(): return 1
    with ZipFile(BASE_DIR/"submission.zip","w",ZIP_DEFLATED) as archive:
        for path in sorted(OUTPUT_DIR.glob("EC_*.json")): archive.write(path, "output/"+path.name)
    print("Created submission.zip"); return 0
if __name__=="__main__": raise SystemExit(main())

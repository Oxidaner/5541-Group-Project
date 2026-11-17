"""Package the verified experiment artifacts without datasets or model weights."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/handoff/HANDOFF_COMP5541_ViT.zip"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    inputs = [
        ROOT / name for name in (
            "README.md", "HANDOFF.md", "Report_结构草稿.md",
            "Group Project.pdf", "docs/protocol.md", "requirements.txt",
            "requirements-lock.txt", "requirements-report.txt",
            "requirements-handoff.txt", "vit_experiment.py", "analyze_results.py",
            "scripts/build_report.py", "scripts/reproduce_experiments.sh",
            "scripts/package_handoff.py",
            "output/pdf/ViT_B32_CIFAR10_Reproduction_Draft.pdf",
        )
    ]
    inputs += [
        item for item in (ROOT / "results").rglob("*")
        if item.is_file()
        and item.suffix in {".json", ".jsonl", ".npz", ".png", ".joblib"}
    ]
    provenance = json.loads((ROOT / "artifacts/pretrained/provenance.json").read_text())
    provenance_path = ROOT / "results/pretrained_provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
    inputs.append(provenance_path)
    files = sorted(set(inputs))
    missing = [str(item.relative_to(ROOT)) for item in files if not item.is_file()]
    if missing:
        raise FileNotFoundError(missing)
    manifest = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(ROOT).as_posix()}"
        for item in files
    ]
    with ZipFile(OUT, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for item in files:
            archive.write(item, item.relative_to(ROOT).as_posix())
        archive.writestr("MANIFEST.sha256", "\n".join(manifest) + "\n")
    with ZipFile(OUT) as archive:
        assert archive.testzip() is None
        assert not any(name.startswith(("data/", "artifacts/", ".venv/"))
                       or name.endswith(".pt") for name in archive.namelist())
        for line in archive.read("MANIFEST.sha256").decode().splitlines():
            expected, name = line.split("  ", 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
        count = len(archive.namelist())
    assert OUT.stat().st_size < 50_000_000
    print(json.dumps({"archive": str(OUT), "files": count,
                      "bytes": OUT.stat().st_size,
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()

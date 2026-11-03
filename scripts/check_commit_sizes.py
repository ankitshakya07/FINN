from pathlib import Path

ROOT = Path(r"c:\Users\Ankit kumar\Downloads\finn_scaffold\finn")

# Get list of files from git dry-run or directory walk excluding gitignored
import subprocess
res = subprocess.run(["git", "add", "-A", "--dry-run"], cwd=str(ROOT), capture_output=True, text=True)
files = [line.replace("add '", "").rstrip("'") for line in res.stdout.splitlines() if line.startswith("add '")]

print(f"Total files to be committed: {len(files)}")
large_files = []
total_bytes = 0
for f in files:
    fp = ROOT / f
    if fp.exists():
        sz = fp.stat().st_size
        total_bytes += sz
        if sz > 500_000: # > 500 KB
            large_files.append((f, sz))

print(f"Total commit size: {total_bytes / (1024*1024):.2f} MB")
print(f"Files over 500KB ({len(large_files)}):")
for f, sz in sorted(large_files, key=lambda x: -x[1]):
    print(f"  {f}: {sz / 1024:.1f} KB")

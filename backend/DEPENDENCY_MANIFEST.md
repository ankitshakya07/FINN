# FINN backend dependency manifest (Windows x64 / CPython 3.12)

This manifest records the direct requirements and the transitive dependency set
families they resolve to. `requirements.txt` intentionally remains the source of
version ranges. Since those ranges are not exact pins, the exact transitive
versions are fixed by the compatible wheelhouse produced for the installation;
do not invent version pins independently of that wheelhouse.

## Direct requirements

| Requirement | Purpose |
| --- | --- |
| `fastapi>=0.115,<1.0` | HTTP API |
| `uvicorn[standard]>=0.30,<1.0` | ASGI server and standard extras |
| `pydantic>=2.8,<3.0` | API models/validation |
| `pydantic-settings>=2.4,<3.0` | Settings support |
| `httpx>=0.27,<1.0` | HTTP client |
| `python-dotenv>=1.0,<2.0` | `.env` support; also requested by Uvicorn standard |
| `yfinance>=0.2.65,<1.0` | Yahoo Finance history fetching |
| `pytest>=8.0,<9.0` | Test runner |

## Transitive dependencies

The resolver installs applicable packages from these families (the exact
version set depends on the versions selected within the ranges above):

- FastAPI: `starlette`, `annotated-doc` (where required), `typing-extensions`.
- Pydantic/settings: `pydantic-core`, `annotated-types`, `typing-inspection`,
  `python-dotenv`.
- Uvicorn standard on Windows: `click`, `h11`, `colorama`, `httptools`,
  `watchfiles`, `websockets`, `PyYAML`, and `python-dotenv`. `uvloop` is not
  applicable on Windows.
- HTTPX: `httpcore`, `anyio`, `certifi`, `idna`, `sniffio`, `h11`,
  `typing-extensions`.
- yfinance: `beautifulsoup4`, `soupsieve`, `curl-cffi`, `cffi`, `pycparser`,
  `lxml`, `multitasking`, `numpy`, `pandas`, `python-dateutil`, `six`, `peewee`,
  `platformdirs`, `protobuf`, `pytz`, `requests`, `charset-normalizer`,
  `urllib3`, `websockets`, and `tzdata` where selected by pandas.
- pytest: `iniconfig`, `packaging`, `pluggy`, `pygments`.

Some names appear in more than one dependency path and are installed once.
This is a dependency graph inventory, not a lock file. `pip download` below
resolves the complete exact set and downloads all artifacts for the target.

`SQLAlchemy` is not in `requirements.txt` and is not used by the backend;
the current repository uses Python's built-in `sqlite3` module.

## Prepare a Windows CPython 3.12 x64 wheelhouse

Run these commands on a network-enabled Windows x64 computer with official
64-bit CPython 3.12. This same-platform method lets pip apply the correct Windows
environment markers. Use `--only-binary=:all:` so a missing compatible wheel is
reported while preparing the wheelhouse, rather than trying to compile on the
offline FINN machine.

```powershell
$Python312 = 'C:\Path\To\Python312\python.exe'
$ProjectRoot = 'C:\Path\To\finn'
$Wheelhouse = Join-Path $ProjectRoot 'backend\wheelhouse'
New-Item -ItemType Directory -Force -Path $Wheelhouse | Out-Null
& $Python312 -m pip download --only-binary=:all: --dest $Wheelhouse `
  --requirement (Join-Path $ProjectRoot 'backend\requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Wheelhouse incomplete: pip could not resolve/download binary wheels.' }
Get-ChildItem $Wheelhouse -Filter '*.whl' | Sort-Object Name | Select-Object -ExpandProperty Name |
  Set-Content (Join-Path $Wheelhouse 'WHEELHOUSE-FILES.txt')
```

Keep the complete `backend\wheelhouse` directory together when transferring it.
The `--only-binary=:all:` resolution is the definitive compatibility check for
the selected versions and Windows x64 target. Upstream PyPI publishes CPython
3.12 Windows x64 wheels for native components such as pandas and Pydantic Core;
curl-cffi provides an `abi3` Windows x64 wheel usable by CPython 3.12, while
pure-Python packages use `py3-none-any` wheels. Check the completed resolver run
for every artifact rather than relying on a manually curated partial list.

## Offline installation on the FINN machine

After official CPython 3.12 x64 and the wheelhouse have been provided, run from
the repository root in PowerShell. Set `$Python312` to the exact standard
CPython executable path. This creates a fresh environment; do not point it at
MSYS2, Windows Store aliases, or an older environment.

```powershell
$Python312 = 'C:\Path\To\Python312\python.exe'
$ProjectRoot = (Get-Location).Path
$Backend = Join-Path $ProjectRoot 'backend'
$Wheelhouse = Join-Path $Backend 'wheelhouse'
& $Python312 -m venv (Join-Path $Backend '.venv')
if ($LASTEXITCODE -ne 0) { throw 'venv creation failed.' }
$VenvPython = Join-Path $Backend '.venv\Scripts\python.exe'
& $VenvPython -m pip install --no-index --find-links $Wheelhouse `
  --requirement (Join-Path $Backend 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Offline dependency installation failed; check wheelhouse completeness.' }
& $VenvPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Installed dependency consistency check failed.' }
Push-Location $Backend
try {
  & $VenvPython -c "import fastapi, pytest; import app.main; print('FastAPI', fastapi.__version__); print('pytest', pytest.__version__); print('app.main import OK')"
  if ($LASTEXITCODE -ne 0) { throw 'Import verification failed.' }
  & $VenvPython -m pytest
  if ($LASTEXITCODE -ne 0) { throw 'pytest suite failed.' }
} finally { Pop-Location }
```

Do not report the environment as installed until all import, `pip check`, and
pytest commands above have actually succeeded.

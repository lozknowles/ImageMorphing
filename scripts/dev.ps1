param(
    [Parameter(Position = 0)]
    [ValidateSet("install", "lint", "format", "test", "check", "run-morph", "run-resize")]
    [string]$Task = "check"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$ruff = Join-Path $root ".venv\Scripts\ruff.exe"
$pytest = Join-Path $root ".venv\Scripts\pytest.exe"

if (-not (Test-Path $python) -and $Task -ne "install") {
    throw "Virtual environment not found. Run: ./scripts/dev.ps1 install"
}

Push-Location $root
try {
    switch ($Task) {
        "install" {
            python -m venv .venv
            & $python -m pip install --upgrade pip
            & $python -m pip install -r requirements-dev.txt
        }
        "lint" {
            & $ruff check --no-cache image_morpher.py resize.py imagemorphing tests
        }
        "format" {
            & $ruff format --no-cache image_morpher.py resize.py imagemorphing tests
        }
        "test" {
            & $python -m pytest -q -p no:cacheprovider
        }
        "check" {
            & $ruff check --no-cache image_morpher.py resize.py imagemorphing tests
            & $ruff format --check --no-cache image_morpher.py resize.py imagemorphing tests
            & $python -m pytest -q -p no:cacheprovider
        }
        "run-morph" {
            & $python image_morpher.py @args[1..($args.Length - 1)]
        }
        "run-resize" {
            & $python resize.py @args[1..($args.Length - 1)]
        }
    }
}
finally {
    Pop-Location
}

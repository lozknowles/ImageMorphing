param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Version,

    [switch]$CreateTag,
    [switch]$Push
)

$ErrorActionPreference = "Stop"

if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    throw "Version must use semantic version format: MAJOR.MINOR.PATCH"
}

$root = Split-Path -Parent $PSScriptRoot
$pyprojectPath = Join-Path $root "pyproject.toml"
$changelogPath = Join-Path $root "CHANGELOG.md"
$git = "C:\Program Files\Git\cmd\git.exe"

Push-Location $root
try {
    $pyproject = Get-Content $pyprojectPath -Raw
    $updatedPyproject = [regex]::Replace(
        $pyproject,
        '(?m)^version = ".*"$',
        "version = `"$Version`""
    )

    if ($updatedPyproject -eq $pyproject) {
        throw "Could not find a version entry in pyproject.toml."
    }

    Set-Content -Path $pyprojectPath -Value $updatedPyproject -Encoding UTF8

    $today = Get-Date -Format "yyyy-MM-dd"
    $changelog = Get-Content $changelogPath -Raw
    $releaseHeader = "## $Version - $today"
    if ($changelog -notmatch [regex]::Escape($releaseHeader)) {
        $updatedChangelog = $changelog -replace '(?m)^# Changelog\r?\n\r?\n', "# Changelog`r`n`r`n$releaseHeader`r`n`r`n- Release preparation.`r`n`r`n"
        Set-Content -Path $changelogPath -Value $updatedChangelog -Encoding UTF8
    }

    & $git diff -- pyproject.toml CHANGELOG.md

    if ($CreateTag) {
        $tagName = "v$Version"
        & $git tag $tagName
        Write-Output "Created tag: $tagName"
        if ($Push) {
            & $git push origin $tagName
        }
    }
}
finally {
    Pop-Location
}

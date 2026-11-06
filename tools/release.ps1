<#
Creates the annotated tag and the GitHub release of backlog-kit from a PC.
Usage (inside the repo, with git and gh installed and `gh auth login` done):
    .\tools\release.ps1            # version read from .claude-plugin/plugin.json
    .\tools\release.ps1 -DryRun    # prints the steps, changes nothing
#>
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'

function Run([string]$what, [scriptblock]$cmd) {
    Write-Host "> $what"
    if (-not $DryRun) { & $cmd; if ($LASTEXITCODE -ne 0) { throw "Failed: $what" } }
}

foreach ($tool in 'git', 'gh') {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "'$tool' is not on PATH." }
}
$root = git rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) { throw 'Run it inside the backlog-kit repo.' }
Set-Location $root

if (git status --porcelain) { throw 'There are uncommitted changes. Commit or discard them first.' }

git fetch origin main --tags --force | Out-Null
git checkout main | Out-Null
git pull --ff-only origin main | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Local main could not be fast-forwarded.' }

$version = (Get-Content .claude-plugin/plugin.json -Raw | ConvertFrom-Json).version
$tag = "v$version"
Write-Host "Version: $version  (tag $tag, commit $(git rev-parse --short HEAD))"

if (git tag --list $tag) { throw "El tag $tag already exists locally." }
if (git ls-remote --tags origin "refs/tags/$tag") { throw "El tag $tag already exists on origin." }

# This version's CHANGELOG section (up to the next "## ")
$lines = Get-Content CHANGELOG.md -Encoding UTF8
$start = ($lines | Select-String -Pattern "^## $([regex]::Escape($version))\s*$" | Select-Object -First 1).LineNumber
if (-not $start) { throw "CHANGELOG.md has no '## $version' heading." }
$body = @()
for ($i = $start; $i -lt $lines.Count -and $lines[$i] -notmatch '^## '; $i++) { $body += $lines[$i] }
$notes = ($body -join "`n").Trim()
if (-not $notes) { throw 'The CHANGELOG section is empty.' }
$notesFile = Join-Path ([System.IO.Path]::GetTempPath()) "backlog-kit-$version-notes.md"
[System.IO.File]::WriteAllText($notesFile, $notes + "`n", (New-Object System.Text.UTF8Encoding($false)))

Write-Host "`nRelease notes:`n$('-' * 40)`n$notes`n$('-' * 40)`n"
if (-not $DryRun) {
    if ((Read-Host "Create tag $tag and the release? (y/N)") -notmatch '^[yY]') { Write-Host 'Cancelled.'; exit 0 }
}

Run "git tag -a $tag -m 'backlog-kit $version'" { git tag -a $tag -m "backlog-kit $version" }
Run "git push origin $tag"                         { git push origin $tag }
Run "gh release create $tag --title $tag"          { gh release create $tag --title $tag --notes-file $notesFile --verify-tag }

if ($DryRun) { Write-Host "`n(DryRun: nothing was created)" } else { Write-Host "`nDone: $(gh release view $tag --json url --jq .url)" }

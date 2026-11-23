# Run the final local suite in order. Keep one log per check.
param([string]$OutputDir = "reports/ui-deep-dive/release")

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

function Invoke-Check([string]$Name, [string]$Program, [string[]]$Arguments) {
    Write-Output "Running $Name"
    $log = Join-Path $OutputDir "$Name.log"
    & $Program @Arguments 2>&1 | Out-File -FilePath $log -Encoding utf8
    if ($LASTEXITCODE) { throw "$Name failed. See $log." }
}

Invoke-Check 'core-offline' 'python' @('-X', 'utf8', 'source/verify.py', (Join-Path $OutputDir 'core-offline.json'))
Invoke-Check 'package' 'node' @('source/verify-independent.cjs')
Invoke-Check 'isolated-runtime' 'node' @('reports/independent-runtime.cjs', '.')
Invoke-Check 'premium-offline' 'python' @('-X', 'utf8', 'source/verify_premium.py')
Invoke-Check 'winter-offline' 'python' @('-X', 'utf8', 'source/verify_winter.py')
Invoke-Check 'app' 'python' @('-X', 'utf8', 'source/verify_ui_app.py', '--layouts')
Invoke-Check 'layout' 'python' @('-X', 'utf8', 'source/verify_ui_layout.py')
Invoke-Check 'atlas' 'python' @('-X', 'utf8', 'source/verify_ui_atlas.py')
Invoke-Check 'stageshow' 'python' @('-X', 'utf8', 'source/verify_ui_stage.py')
Invoke-Check 'local-guides' 'python' @('-X', 'utf8', 'source/verify_guided.py')
Get-FileHash -Algorithm SHA256 index.html,docs/index.html,docs/offline.html |
    Select-Object Hash, Path | ConvertTo-Json | Out-File (Join-Path $OutputDir 'hashes.json') -Encoding utf8
Write-Output 'Finished ten checks in sequence.'

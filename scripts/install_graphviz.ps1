<#
.SYNOPSIS
  Install Graphviz with winget and add Graphviz\bin to PATH.

.DESCRIPTION
  Installs Graphviz.Graphviz using winget, then ensures the Graphviz bin directory
  is placed at the front of the selected PATH scope so `dot` resolves to the
  newly installed Graphviz first.

.EXAMPLES
  # Recommended: run PowerShell as Administrator and add to system PATH
  powershell -ExecutionPolicy Bypass -File .\scripts\install_graphviz.ps1

  # Add to current user's PATH when not running as Administrator
  powershell -ExecutionPolicy Bypass -File .\scripts\install_graphviz.ps1 -PathScope User

  # Show installer UI if you want to select install options manually
  powershell -ExecutionPolicy Bypass -File .\scripts\install_graphviz.ps1 -Interactive
#>
[CmdletBinding()]
param(
    [ValidateSet('Machine', 'User')]
    [string]$PathScope = 'Machine',

    [string]$PackageId = 'Graphviz.Graphviz',

    [string]$GraphvizBin = 'C:\Program Files\Graphviz\bin',

    [switch]$Interactive,

    [switch]$SkipInstall
)

$ErrorActionPreference = 'Stop'

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Normalize-PathEntry([string]$PathEntry) {
    if ([string]::IsNullOrWhiteSpace($PathEntry)) { return '' }
    return ($PathEntry.Trim().TrimEnd('\'))
}

function Add-BinToPathFirst {
    param(
        [Parameter(Mandatory=$true)][string]$BinPath,
        [Parameter(Mandatory=$true)][ValidateSet('Machine','User')][string]$Scope
    )

    if (-not (Test-Path -LiteralPath $BinPath)) {
        throw "Graphviz bin path does not exist: $BinPath"
    }

    $currentPath = [Environment]::GetEnvironmentVariable('Path', $Scope)
    if ($null -eq $currentPath) { $currentPath = '' }

    $targetNorm = Normalize-PathEntry $BinPath
    $entries = $currentPath -split ';' |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Where-Object { (Normalize-PathEntry $_) -ine $targetNorm }

    $newPath = (@($BinPath) + @($entries)) -join ';'
    [Environment]::SetEnvironmentVariable('Path', $newPath, $Scope)

    # Make this PowerShell session see the change immediately as well.
    $processEntries = $env:Path -split ';' |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Where-Object { (Normalize-PathEntry $_) -ine $targetNorm }
    $env:Path = (@($BinPath) + @($processEntries)) -join ';'
}

if ($PathScope -eq 'Machine' -and -not (Test-IsAdministrator)) {
    throw "Adding Graphviz to the system PATH requires Administrator PowerShell. Re-run as Administrator, or use -PathScope User."
}

if (-not $SkipInstall) {
    $installed = $false
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        $wingetBaseArgs = @('install', '--id', $PackageId, '--exact', '--accept-package-agreements', '--accept-source-agreements')
        $wingetAttempts = @()
        if ($Interactive) {
            $wingetAttempts += ,($wingetBaseArgs + @('--interactive'))
        } else {
            $installScope = if (Test-IsAdministrator) { 'machine' } else { 'user' }
            $wingetAttempts += ,($wingetBaseArgs + @('--silent', '--scope', $installScope))
            $wingetAttempts += ,($wingetBaseArgs + @('--silent'))
            $wingetAttempts += ,($wingetBaseArgs)
        }

        foreach ($wingetArgs in $wingetAttempts) {
            Write-Host "Installing Graphviz with winget package: $PackageId"
            Write-Host "winget $($wingetArgs -join ' ')"
            & winget @wingetArgs
            if ($LASTEXITCODE -eq 0) {
                $installed = $true
                break
            }
            Write-Warning "winget install attempt failed with exit code $LASTEXITCODE"
        }
    } else {
        Write-Warning 'winget was not found.'
    }

    if (-not $installed) {
        $choco = Get-Command choco -ErrorAction SilentlyContinue
        if ($choco) {
            Write-Host 'Installing Graphviz with Chocolatey package: graphviz'
            & choco install graphviz -y --no-progress
            if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 3010) {
                $installed = $true
            } else {
                Write-Warning "choco install failed with exit code $LASTEXITCODE"
            }
        } else {
            Write-Warning 'Chocolatey was not found.'
        }
    }

    if (-not $installed) {
        throw 'Graphviz automatic installation failed. Tried winget and Chocolatey.'
    }
}

# Prefer the standard winget location, but fall back to the first dot.exe found in common locations.
if (-not (Test-Path -LiteralPath (Join-Path $GraphvizBin 'dot.exe'))) {
    $fixedCandidates = @(
        'C:\Program Files\Graphviz\bin\dot.exe',
        'C:\Program Files (x86)\Graphviz\bin\dot.exe',
        "$env:LOCALAPPDATA\Programs\Graphviz\bin\dot.exe",
        'E:\Graphviz\bin\dot.exe',
        'C:\ProgramData\chocolatey\bin\dot.exe'
    )

    $searchRoots = @(
        'C:\Program Files\Graphviz',
        'C:\Program Files (x86)\Graphviz',
        "$env:LOCALAPPDATA\Programs\Graphviz",
        "$env:ChocolateyInstall\lib\graphviz",
        'C:\ProgramData\chocolatey\lib\graphviz'
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and (Test-Path -LiteralPath $_) }

    $discoveredCandidates = @()
    foreach ($root in $searchRoots) {
        $discoveredCandidates += Get-ChildItem -LiteralPath $root -Recurse -Filter dot.exe -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty FullName
    }

    $candidate = @($fixedCandidates + $discoveredCandidates) |
        Where-Object { Test-Path -LiteralPath $_ } |
        Select-Object -First 1

    if ($candidate) {
        $GraphvizBin = Split-Path -Parent $candidate
    }
}

Add-BinToPathFirst -BinPath $GraphvizBin -Scope $PathScope

Write-Host "Graphviz bin added to $PathScope PATH first: $GraphvizBin"
Write-Host 'Verifying dot resolution:'
where.exe dot
& dot -V

Write-Host ''
Write-Host 'If an already-open terminal still uses an old dot.exe, close it and open a new terminal.'


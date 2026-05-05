# check-frontend.ps1
#
# Validates the SvelteKit frontend before Docker build.
#
# MODES (choose one):
#   .\check-frontend.ps1              # FULL check: svelte-check + vite build
#   .\check-frontend.ps1 -Quick       # Quick: vite build only (fastest Docker mirror)
#   .\check-frontend.ps1 -TypeCheck   # svelte-check only (all TS + Svelte errors)
#
# FLAGS:
#   -Install   Force reinstall node_modules first
#   -Bail      Stop immediately on first failure
#
# EXIT CODES:
#   0 = everything passed
#   1 = at least one check failed
#
# WHAT BLOCKS DOCKER:
#   Svelte compiler errors (svelte) -> vite build fails -> Docker fails
#   TypeScript errors (ts) -> svelte-check only, vite build does NOT type-check
#   Warnings (Warn:) -> never block Docker

param(
    [switch]$Quick,
    [switch]$TypeCheck,
    [switch]$Install,
    [switch]$Bail
)

$ErrorActionPreference = 'Stop'

function Write-Banner([string]$text) {
    Write-Host ''
    Write-Host ('=' * 64) -ForegroundColor DarkCyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host ('=' * 64) -ForegroundColor DarkCyan
}

function Write-Step([string]$text) {
    Write-Host ''
    Write-Host ">> $text" -ForegroundColor Yellow
}

function Write-Pass([string]$text) { Write-Host "  [PASS] $text" -ForegroundColor Green }
function Write-Fail([string]$text) { Write-Host "  [FAIL] $text" -ForegroundColor Red }
function Write-Info([string]$text) { Write-Host "  $text" -ForegroundColor Gray }

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $projectRoot 'frontend'
$binDir      = Join-Path $frontendDir 'node_modules\.bin'
$ext         = if ($IsWindows -or $env:OS -eq 'Windows_NT') { '.CMD' } else { '' }
$svelteCheck = Join-Path $binDir "svelte-check$ext"
$svelteKit   = Join-Path $binDir "svelte-kit$ext"
$vite        = Join-Path $binDir "vite$ext"

if (-not (Test-Path $frontendDir)) {
    Write-Fail "Cannot find frontend/ at $frontendDir"
    exit 1
}

# Determine mode label
if ($Quick) {
    $modeLabel = 'Quick  - vite build only (exact Docker mirror)'
} elseif ($TypeCheck) {
    $modeLabel = 'TypeCheck - svelte-check only (TS + Svelte errors)'
} else {
    $modeLabel = 'Full   - svelte-check + vite build'
}

Write-Banner 'Frontend Pre-Build Validator'
Write-Info "Project : $projectRoot"
Write-Info "Mode    : $modeLabel"
Write-Info ''
Write-Info 'What blocks Docker:'
Write-Info '  Svelte compiler errors  -> vite build fails  -> Docker fails'
Write-Info '  TypeScript (ts) errors  -> svelte-check only, vite does NOT type-check'
Write-Info '  Warnings                -> never block Docker'

# ---------------------------------------------------------------------------
# Step 1: Install node_modules if needed
# ---------------------------------------------------------------------------

$needInstall = $Install -or (-not (Test-Path $binDir)) -or (-not (Test-Path $vite))
if ($needInstall) {
    Write-Step 'Installing node_modules...'
    Push-Location $frontendDir
    try {
        $prevEA = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        corepack enable 2>&1 | Out-Null
        corepack prepare pnpm@10.14.0 --activate 2>&1 | Out-Null
        $ErrorActionPreference = $prevEA

        $pnpmCmd = Get-Command pnpm -ErrorAction SilentlyContinue
        if ($pnpmCmd) {
            Write-Info 'Using pnpm...'
            & pnpm install --frozen-lockfile
        } else {
            Write-Info 'pnpm unavailable after corepack, falling back to npm ci'
            & npm ci
        }
        if ($LASTEXITCODE -ne 0) { Write-Fail "Install failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }
        Write-Pass 'node_modules installed'
    } finally { Pop-Location }
} else {
    Write-Pass 'node_modules present  (-Install to force refresh)'
}

# ---------------------------------------------------------------------------
# Step 2: svelte-kit sync  (generates .svelte-kit/tsconfig.json)
#         Needed by both svelte-check and vite build
# ---------------------------------------------------------------------------

Write-Step 'svelte-kit sync...'
Push-Location $frontendDir
try {
    if (Test-Path $svelteKit) {
        $prevEA = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $svelteKit sync 2>&1 | Out-Null
        $ErrorActionPreference = $prevEA
        Write-Pass 'svelte-kit sync done'
    } else {
        Write-Info 'svelte-kit not found - skipping (tsconfig.json warning may appear)'
    }
} finally { Pop-Location }

# ---------------------------------------------------------------------------
# Step 3: svelte-check  (skip in -Quick mode)
# Reports:
#   (svelte) errors  -> Svelte compiler errors, WILL block vite / Docker
#   (ts) errors      -> TypeScript type errors, will NOT block vite / Docker
#   Warn             -> warnings, never block Docker
# ---------------------------------------------------------------------------

$checkExit = 0
if (-not $Quick) {
    Write-Step 'svelte-check (TypeScript + Svelte compiler + a11y)...'
    Write-Info 'Labels: (svelte) = blocks Docker | (ts) = type-only | Warn = never blocks'
    Write-Host ''
    Push-Location $frontendDir
    try {
        $prevEA = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $svelteCheck --tsconfig ./tsconfig.json --output human --threshold warning
        $checkExit = $LASTEXITCODE
        $ErrorActionPreference = $prevEA
    } finally { Pop-Location }

    if ($checkExit -eq 0) {
        Write-Pass 'svelte-check: no errors'
    } else {
        Write-Fail "svelte-check: errors found (exit $checkExit)"
        Write-Info 'Note: (ts) errors above do NOT block Docker. Only (svelte) errors do.'
        if ($Bail) {
            Write-Host ''
            Write-Host 'Stopped (-Bail). Fix Svelte compiler errors before building.' -ForegroundColor Red
            exit $checkExit
        }
    }
}

# ---------------------------------------------------------------------------
# Step 4: vite build  (skip in -TypeCheck mode)
# This is the EXACT command Docker runs. If this passes, Docker will pass.
# ---------------------------------------------------------------------------

$buildExit = 0
if (-not $TypeCheck) {
    Write-Step 'vite build  (exact Docker mirror)...'
    Write-Info 'If this passes, the Docker build will pass.'
    Write-Host ''
    if (-not (Test-Path $vite)) {
        Write-Fail "vite not found at $vite - run with -Install first"
        exit 1
    }
    Push-Location $frontendDir
    try {
        $prevEA = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $vite build
        $buildExit = $LASTEXITCODE
        $ErrorActionPreference = $prevEA
    } finally { Pop-Location }

    if ($buildExit -eq 0) {
        Write-Pass 'vite build: success'
    } else {
        Write-Fail "vite build: FAILED - this is exactly what broke Docker"
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

Write-Banner 'Results'

if (-not $Quick) {
    $lbl = if ($checkExit -eq 0) { 'PASS' } else { 'FAIL' }
    $col = if ($checkExit -eq 0) { 'Green' } else { 'Red' }
    Write-Host '  svelte-check : ' -NoNewline
    Write-Host $lbl -ForegroundColor $col
    if ($checkExit -ne 0) {
        Write-Host '                 (ts) errors = TypeScript only, do NOT block Docker' -ForegroundColor DarkGray
        Write-Host '                 (svelte) errors = WILL block Docker' -ForegroundColor DarkGray
    }
}

if (-not $TypeCheck) {
    $lbl = if ($buildExit -eq 0) { 'PASS' } else { 'FAIL' }
    $col = if ($buildExit -eq 0) { 'Green' } else { 'Red' }
    Write-Host '  vite build   : ' -NoNewline
    Write-Host $lbl -ForegroundColor $col
    if ($buildExit -eq 0) {
        Write-Host '                 Docker build will succeed.' -ForegroundColor DarkGray
    }
}

Write-Host ''
$dockerFailed = $buildExit -ne 0
$anyFailed    = $dockerFailed -or ($checkExit -ne 0)

if ($dockerFailed) {
    Write-Host '  DOCKER BUILD WILL FAIL - fix vite build errors first.' -ForegroundColor Red
} elseif (-not $TypeCheck -and $checkExit -ne 0) {
    Write-Host '  Docker build will SUCCEED but TypeScript/a11y issues exist.' -ForegroundColor Yellow
    Write-Host '  Consider fixing (ts) and (svelte) warnings over time.' -ForegroundColor DarkGray
} else {
    Write-Host '  All checks passed - safe to build.' -ForegroundColor Green
}

Write-Host ''
exit $(if ($anyFailed) { 1 } else { 0 })

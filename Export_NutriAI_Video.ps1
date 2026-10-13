##############################################################################
# Export_NutriAI_Video.ps1
# ─────────────────────────────────────────────────────────────────────────────
# Exports NutriAI_Presentation.pptx → NutriAI_Video.mp4  (Full HD 1080p)
# Duration: 150 seconds  (20 slides × 7.5 s each)
#
# WHAT THIS SCRIPT DOES:
#   1. Installs python-pptx if not present
#   2. Runs set_timings.py to embed 7.5s advance timing on every slide
#   3. Opens PowerPoint via COM automation
#   4. Exports the presentation as Full HD 1080p MP4 video
#   5. Waits for the export to complete
#   6. Confirms the output file
#
# REQUIREMENTS:
#   - Microsoft PowerPoint 2016 / 2019 / 2021 / 365 must be installed
#   - Python 3.9+ must be installed and in PATH
#   - Run from the nutrition-ai folder
#
# USAGE:
#   cd nutrition-ai
#   PowerShell -ExecutionPolicy Bypass -File Export_NutriAI_Video.ps1
##############################################################################

$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$PptxFile    = Join-Path $ScriptDir "NutriAI_Presentation.pptx"
$VideoFile   = Join-Path $ScriptDir "NutriAI_Video.mp4"
$TimingScript = Join-Path $ScriptDir "set_timings.py"

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   🎬  NutriAI — Video Export Script                 ║" -ForegroundColor Cyan
Write-Host "  ║   PPTX → MP4  |  150s  |  1080p Full HD            ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Verify PPTX exists ────────────────────────────────────────────────
if (-not (Test-Path $PptxFile)) {
    Write-Host "  ERROR: NutriAI_Presentation.pptx not found at:" -ForegroundColor Red
    Write-Host "         $PptxFile" -ForegroundColor Red
    Write-Host "  Make sure you are running this script from the nutrition-ai folder." -ForegroundColor Yellow
    pause; exit 1
}
Write-Host "  [1/4] Found: $PptxFile" -ForegroundColor Green

# ── Step 2: Install python-pptx and set timings ───────────────────────────────
Write-Host "  [2/4] Setting 7.5s slide timings (150s total)..." -ForegroundColor Cyan
try {
    python -c "import pptx" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "        Installing python-pptx..." -ForegroundColor Yellow
        pip install python-pptx --quiet
    }
    Push-Location $ScriptDir
    python set_timings.py
    Pop-Location
    Write-Host "        Timings applied successfully." -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Could not run set_timings.py — $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "           Continuing with existing timings..." -ForegroundColor Yellow
}

# ── Step 3: Verify PowerPoint is installed ────────────────────────────────────
Write-Host "  [3/4] Starting PowerPoint COM automation..." -ForegroundColor Cyan
try {
    $pptApp = New-Object -ComObject PowerPoint.Application
} catch {
    Write-Host ""
    Write-Host "  ERROR: Microsoft PowerPoint is not installed or COM automation failed." -ForegroundColor Red
    Write-Host ""
    Write-Host "  MANUAL EXPORT INSTRUCTIONS:" -ForegroundColor Yellow
    Write-Host "  ─────────────────────────────────────────────────────────────────"
    Write-Host "  1. Open NutriAI_Presentation.pptx in PowerPoint"
    Write-Host "  2. Click:  File → Export → Create a Video"
    Write-Host "  3. Quality: Full HD (1080p)"
    Write-Host "  4. Timing:  Use Recorded Timings and Narrations"
    Write-Host "              (or 'Don't Use Recorded Timings' → set 7.5 seconds)"
    Write-Host "  5. Click:   Create Video"
    Write-Host "  6. Save as: NutriAI_Video.mp4"
    Write-Host "  ─────────────────────────────────────────────────────────────────"
    Write-Host ""
    pause; exit 1
}

# ── Step 4: Export as video ───────────────────────────────────────────────────
Write-Host "  [4/4] Exporting as MP4 video (this may take 1-3 minutes)..." -ForegroundColor Cyan
Write-Host "        Output: $VideoFile" -ForegroundColor White

try {
    $pptApp.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

    # Open the presentation
    $pres = $pptApp.Presentations.Open($PptxFile, $false, $false, $true)

    # CreateVideo parameters:
    #   FileName, UseTimingsAndNarrations, DefaultSlideDuration,
    #   VertResolution, FramesPerSecond, Quality
    #
    # UseTimingsAndNarrations = $true  → use the 7.5s timings we set
    # DefaultSlideDuration    = 7.5    → fallback if timing not found
    # VertResolution          = 1080   → Full HD
    # FramesPerSecond         = 30
    # Quality                 = 85

    $pres.CreateVideo(
        $VideoFile,   # FileName
        $true,        # UseTimingsAndNarrations
        7,            # DefaultSlideDuration (seconds, integer)
        1080,         # VertResolution (Full HD)
        30,           # FramesPerSecond
        85            # Quality (1-100)
    )

    Write-Host "        Export started — polling for completion..." -ForegroundColor White

    # Poll until export state = ppMediaTaskStatusDone (3) or Failed (4)
    $timeout = 300  # 5 minutes max
    $elapsed = 0
    do {
        Start-Sleep -Seconds 3
        $elapsed += 3
        $state = $pres.CreateVideoStatus
        $dots  = "." * (($elapsed / 3) % 6 + 1)
        Write-Host "        Exporting$dots ($elapsed s)" -ForegroundColor Gray -NoNewline
        Write-Host "`r" -NoNewline
    } while ($state -ne 3 -and $state -ne 4 -and $elapsed -lt $timeout)

    Write-Host ""

    if ($state -eq 3) {
        Write-Host ""
        Write-Host "  ══════════════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host "   ✅  Export SUCCESS!" -ForegroundColor Green
        $sizeMB = [math]::Round((Get-Item $VideoFile).Length / 1MB, 1)
        Write-Host "   📹  NutriAI_Video.mp4  ($sizeMB MB)" -ForegroundColor Green
        Write-Host "   ⏱️   Duration: ~150 seconds  |  1080p Full HD  |  30fps" -ForegroundColor Green
        Write-Host "  ══════════════════════════════════════════════════════════" -ForegroundColor Green
    } elseif ($state -eq 4) {
        Write-Host "  ERROR: PowerPoint reported export failure (state=4)." -ForegroundColor Red
        Write-Host "         Try exporting manually: File → Export → Create a Video" -ForegroundColor Yellow
    } else {
        Write-Host "  WARNING: Export timed out. Check if the video file was created:" -ForegroundColor Yellow
        Write-Host "           $VideoFile" -ForegroundColor Yellow
    }

} catch {
    Write-Host "  ERROR during export: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Clean up COM objects
    if ($pres) {
        try { $pres.Close() } catch {}
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
    }
    if ($pptApp) {
        try { $pptApp.Quit() } catch {}
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pptApp) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

Write-Host ""
Write-Host "  Done. Video file location:" -ForegroundColor Cyan
Write-Host "  $VideoFile" -ForegroundColor White
Write-Host ""
pause

##############################################################################
# deploy_to_github.ps1
# ─────────────────────────────────────────────────────────────────────────────
# Deploys all NutriAI project files to GitHub via the GitHub Contents API.
# No git client required — uses PowerShell + GitHub REST API.
#
# USAGE:
#   1. Open PowerShell in this folder (nutrition-ai)
#   2. Run: .\deploy_to_github.ps1 -Token "ghp_your_token_here"
#
# HOW TO GET A TOKEN:
#   1. Go to https://github.com/settings/tokens/new
#   2. Select scopes: repo (full), workflow
#   3. Generate and copy the token
#   4. Paste it in the command above
##############################################################################

param(
    [Parameter(Mandatory=$true)]
    [string]$Token,
    [string]$Owner  = "dixit1948",
    [string]$Repo   = "Nutrition-Agentic-AI",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
$BaseUrl = "https://api.github.com/repos/$Owner/$Repo/contents"

$Headers = @{
    "Authorization" = "token $Token"
    "Accept"        = "application/vnd.github.v3+json"
    "User-Agent"    = "NutriAI-Deploy-Script"
}

# ── Files to upload (path in repo => local path) ─────────────────────────────
$Files = @{
    "README.md"                    = "README.md"
    "requirements.txt"             = "requirements.txt"
    ".gitignore"                   = ".gitignore"
    ".env.example"                 = ".env.example"
    "LICENSE"                      = "LICENSE"
    "app.py"                       = "app.py"
    "agent.py"                     = "agent.py"
    "granite_client.py"            = "granite_client.py"
    "guardrails.py"                = "guardrails.py"
    "plan_saver.py"                = "plan_saver.py"
    "run.bat"                      = "run.bat"
    "sample_plan_output.md"        = "sample_plan_output.md"
    "static/index.html"            = "static\index.html"
    "static/style.css"             = "static\style.css"
    "static/app.js"                = "static\app.js"
}

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   🥗  NutriAI — GitHub Deployment Script            ║" -ForegroundColor Cyan
Write-Host "  ║   Uploading to: https://github.com/$Owner/$Repo  ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$Uploaded  = 0
$Failed    = 0
$Total     = $Files.Count

foreach ($Entry in $Files.GetEnumerator()) {
    $RepoPath  = $Entry.Key
    $LocalPath = $Entry.Value

    if (-not (Test-Path $LocalPath)) {
        Write-Host "  [SKIP] $RepoPath — local file not found" -ForegroundColor Yellow
        continue
    }

    # Read file as base64
    $FileBytes   = [System.IO.File]::ReadAllBytes((Resolve-Path $LocalPath))
    $Base64Content = [Convert]::ToBase64String($FileBytes)

    # Check if file already exists in repo (to get SHA for update)
    $ExistingSha = $null
    try {
        $Existing    = Invoke-RestMethod -Uri "$BaseUrl/$RepoPath" -Headers $Headers -Method Get
        $ExistingSha = $Existing.sha
    } catch { }

    # Build request body
    $Body = @{
        message = "Add $RepoPath — NutriAI IBM Granite Nutrition Agent"
        content = $Base64Content
        branch  = $Branch
    }
    if ($ExistingSha) {
        $Body["sha"]     = $ExistingSha
        $Body["message"] = "Update $RepoPath — NutriAI IBM Granite Nutrition Agent"
    }

    try {
        $null = Invoke-RestMethod `
            -Uri     "$BaseUrl/$RepoPath" `
            -Headers $Headers `
            -Method  Put `
            -Body    ($Body | ConvertTo-Json -Depth 5) `
            -ContentType "application/json"

        $Action = if ($ExistingSha) { "Updated" } else { "Uploaded" }
        Write-Host "  [OK] $Action  $RepoPath" -ForegroundColor Green
        $Uploaded++
    } catch {
        Write-Host "  [ERR] Failed $RepoPath — $($_.Exception.Message)" -ForegroundColor Red
        $Failed++
    }
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Deployment complete!" -ForegroundColor Cyan
Write-Host "  Uploaded : $Uploaded / $Total files" -ForegroundColor Green
if ($Failed -gt 0) {
    Write-Host "  Failed   : $Failed files" -ForegroundColor Red
}
Write-Host ""
Write-Host "  Repository: https://github.com/$Owner/$Repo" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""

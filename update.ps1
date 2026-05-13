Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Join-Path $scriptDir "logs"
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
$logPath = Join-Path $logDir "update.log"
$transcriptStarted = $false

try {
    Start-Transcript -Path $logPath -Append | Out-Null
    $transcriptStarted = $true
}
catch {
    Write-Host "Не удалось включить логирование в $logPath" -ForegroundColor Yellow
}

function Test-CommandExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-CommandChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$ErrorMessage
    )

    Write-Host "> $FilePath $($Arguments -join ' ')"
    & $FilePath @Arguments
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        throw "$ErrorMessage Код: $exitCode."
    }
}

function Get-ComposeFilePath {
    $candidates = @(
        (Join-Path $scriptDir "docker-compose.yaml"),
        (Join-Path $scriptDir "docker-compose.yml"),
        (Join-Path $scriptDir "compose.yaml"),
        (Join-Path $scriptDir "compose.yml")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    throw "Файл docker compose не найден рядом со скриптом."
}

function Test-ComposeUsesLocalBuild {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComposePath
    )

    $composeText = Get-Content -LiteralPath $ComposePath -Raw
    return $composeText -match '(?m)^\s+build\s*:'
}

function Test-GitRepository {
    return Test-Path -LiteralPath (Join-Path $scriptDir ".git")
}

Push-Location $scriptDir

try {
    if (-not (Test-CommandExists -Name "docker")) {
        throw "Docker CLI не найден."
    }

    Invoke-CommandChecked -FilePath "docker" -Arguments @("compose", "version") -ErrorMessage "Плагин docker compose недоступен."

    $composePath = Get-ComposeFilePath
    $usesLocalBuild = Test-ComposeUsesLocalBuild -ComposePath $composePath

    if ($usesLocalBuild) {
        Write-Host "Найден build в $([System.IO.Path]::GetFileName($composePath)). Будет локальная пересборка контейнера." -ForegroundColor Cyan

        if (Test-GitRepository) {
            if (-not (Test-CommandExists -Name "git")) {
                throw "В каталоге есть git-репозиторий, но команда git недоступна."
            }

            Invoke-CommandChecked -FilePath "git" -Arguments @("pull", "--ff-only") -ErrorMessage "Не удалось получить последние изменения из git."
        }
        else {
            Write-Host "Git-репозиторий не найден. Пересобираю текущую локальную копию без git pull." -ForegroundColor Yellow
        }

        Invoke-CommandChecked -FilePath "docker" -Arguments @("compose", "up", "-d", "--build") -ErrorMessage "Не удалось пересобрать и перезапустить контейнеры."
    }
    else {
        Write-Host "Compose использует готовые образы. Будет выполнен pull и перезапуск контейнеров." -ForegroundColor Cyan
        Invoke-CommandChecked -FilePath "docker" -Arguments @("compose", "pull") -ErrorMessage "Не удалось скачать свежие образы."
        Invoke-CommandChecked -FilePath "docker" -Arguments @("compose", "up", "-d") -ErrorMessage "Не удалось перезапустить контейнеры."
    }

    Write-Host "Обновление завершено." -ForegroundColor Green
    Write-Host "Лог сохранен в $logPath" -ForegroundColor Green
}
catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "Лог сохранен в $logPath" -ForegroundColor Yellow
    exit 1
}
finally {
    if ($transcriptStarted) {
        Stop-Transcript | Out-Null
    }
    Pop-Location
}

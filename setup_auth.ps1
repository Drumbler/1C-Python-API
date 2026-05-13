param(
    [string]$Registry = "ghcr.io",
    [string]$Username,
    [SecureString]$Token
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logDir = Join-Path $scriptDir "logs"
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
$logPath = Join-Path $logDir "setup_auth.log"
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

function Convert-SecureStringToPlainText {
    param(
        [Parameter(Mandatory = $true)]
        [SecureString]$SecureValue
    )

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

function Invoke-DockerLogin {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Registry,
        [Parameter(Mandatory = $true)]
        [string]$Username,
        [Parameter(Mandatory = $true)]
        [SecureString]$Token
    )

    $plainToken = Convert-SecureStringToPlainText -SecureValue $Token
    try {
        Write-Host "> docker login $Registry --username $Username --password-stdin"
        $plainToken | docker login $Registry --username $Username --password-stdin | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "docker login завершился с ошибкой."
        }
    }
    finally {
        $plainToken = $null
    }
}

try {
    if (-not (Test-CommandExists -Name "docker")) {
        throw "Docker CLI не найден."
    }

    if ([string]::IsNullOrWhiteSpace($Username)) {
        $Username = Read-Host "GitHub username для $Registry"
    }

    if ([string]::IsNullOrWhiteSpace($Username)) {
        throw "Имя пользователя не задано."
    }

    if ($null -eq $Token) {
        $Token = Read-Host "GitHub PAT с read:packages" -AsSecureString
    }

    Invoke-DockerLogin -Registry $Registry -Username $Username -Token $Token

    Write-Host "Авторизация в $Registry завершена." -ForegroundColor Green
    Write-Host "Если используется Docker Desktop, credentials обычно сохраняются автоматически." -ForegroundColor Green
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
}

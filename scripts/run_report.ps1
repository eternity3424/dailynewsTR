# Gunluk Haber Bulteni - Windows Gorev Zamanlayici calistiricisi
#
# GitHub Actions'in cron zamanlayicisi bu repoda guvenilir olmadigi icin
# bulten bu bilgisayarda uretilir. Gorev Zamanlayici bu betigi 08:13 ve
# 20:07'de (Windows yerel saati) calistirir.
#
# Kullanim (elle denemek icin):
#   powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode morning
#   powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode evening
#   powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode morning -Test
#
# Yaptigi isler:
#   1. Git deposunu gunceller (pull --ff-only)
#   2. Sanal ortam python'u ile bulteni uretir ve GERCEK e-posta gonderir
#   3. data/ dosyalarini commit edip push eder (hikaye takibi / quiz gecmisi)
#   4. Her seyi logs/ altindaki dosyaya UTF-8 olarak yazar
#
# DIKKAT - bu dosya bilerek TAMAMEN ASCII karakterlerle yazilmistir.
# PowerShell 5.1, BOM'suz UTF-8 dosyalardaki Turkce harfleri bozuyor.
# Ayni sebepten yerel komut ciktisi Start-Process ile bayt duzeyinde
# yakalanip UTF-8 olarak okunur; aksi halde emoji ve Turkce karakterler
# log dosyasinda '?' olarak kayboluyordu.

[CmdletBinding()]
param(
    [ValidateSet('morning', 'evening')]
    [string]$Mode = 'morning',

    # Test modu: e-posta gondermez, HTML dosyaya yazar
    [switch]$Test,

    # Git degisikliklerini commit/push etme
    [switch]$SkipGit
)

$ErrorActionPreference = 'Stop'

# --- Yollar ---
$RepoRoot  = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$LogDir    = Join-Path $RepoRoot 'logs'

Set-Location $RepoRoot

if (-not (Test-Path -LiteralPath $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$LogFile = Join-Path $LogDir ("run_{0}_{1}.log" -f $Mode, (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $line = "{0} [{1}] {2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Level, $Message
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Invoke-Native {
    <#
    Yerel bir komutu calistirir, ciktisini UTF-8 olarak log dosyasina yazar
    ve cikis kodunu dondurur.

    Iki sorunu cozer:
      * PowerShell, yerel komutlarin stderr ciktisini ErrorRecord'a cevirip
        $ErrorActionPreference='Stop' iken betigi durduruyordu.
      * Ciktiyi dogrudan 2>&1 ile okumak, konsol kodlamasindan gecirdigi
        icin Turkce harfleri ve emojileri bozuyordu. Start-Process ciktiyi
        dogrudan dosyaya bayt duzeyinde yazar, boylece bu sorun olusmaz.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [switch]$Quiet
    )

    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()

    try {
        # Start-Process diziyi boslukla birlestirir; bosluk iceren
        # argumanlarin tirnaklanmasi gerekir.
        $argString = ''
        if ($Arguments.Count -gt 0) {
            $argString = ($Arguments | ForEach-Object {
                if ($_ -match '\s') { '"' + $_ + '"' } else { $_ }
            }) -join ' '
        }

        if (-not $Quiet) {
            Write-Log ("$ " + (Split-Path -Leaf $FilePath) + " " + $argString)
        }

        $proc = Start-Process -FilePath $FilePath `
                               -ArgumentList $argString `
                               -NoNewWindow -Wait -PassThru `
                               -RedirectStandardOutput $outFile `
                               -RedirectStandardError $errFile

        foreach ($f in @($outFile, $errFile)) {
            if ((Get-Item -LiteralPath $f).Length -gt 0) {
                foreach ($l in [System.IO.File]::ReadAllLines($f, [System.Text.Encoding]::UTF8)) {
                    Add-Content -Path $LogFile -Value $l -Encoding UTF8
                }
            }
        }
        return $proc.ExitCode
    } finally {
        Remove-Item -LiteralPath $outFile, $errFile -Force -ErrorAction SilentlyContinue
    }
}

# --- On kontroller ---
if (-not (Test-Path -LiteralPath $PythonExe)) {
    Write-Log "Sanal ortam bulunamadi: $PythonExe" 'ERROR'
    Write-Log "Olusturmak icin: py -3.12 -m venv .venv" 'ERROR'
    exit 1
}

$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUNBUFFERED = '1'

Write-Log '==============================================='
if ($Test) {
    Write-Log "Mod: $Mode  (TEST - mail gonderilmez)"
} else {
    Write-Log "Mod: $Mode  (mail gonderilecek)"
}
Write-Log "Kok dizin : $RepoRoot"
Write-Log "Python    : $PythonExe"
Write-Log "Log       : $LogFile"

# --- 1. Repo guncelle ---
if (-not $SkipGit) {
    $code = Invoke-Native -FilePath 'git' -Arguments @('pull', '--ff-only')
    if ($code -ne 0) {
        Write-Log "git pull basarisiz (exit $code). Rapor yine de calistirilacak." 'WARN'
    }
}

# --- 2. Bulteni uret ve gonder ---
$pyArgs = @('-m', 'src.main', '--mode', $Mode)
if ($Test) { $pyArgs += '--test' }

Write-Log ("Calistiriliyor: python " + ($pyArgs -join ' '))
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$pyExit = Invoke-Native -FilePath $PythonExe -Arguments $pyArgs -Quiet
$sw.Stop()

Write-Log ("Sure: {0:N1} saniye" -f $sw.Elapsed.TotalSeconds)

if ($pyExit -ne 0) {
    Write-Log "Bulten basarisiz (cikis kodu $pyExit)." 'ERROR'
    Write-Log "Ayrinti icin: $LogFile" 'ERROR'
    exit $pyExit
}
Write-Log 'Bulten basariyla tamamlandi.' 'OK'

# --- 3. data/ dosyalarini geri gonder ---
if (-not $SkipGit -and -not $Test) {
    Write-Log 'data/ degisiklikleri kontrol ediliyor...'
    [void](Invoke-Native -FilePath 'git' -Arguments @('add', 'data/') -Quiet)

    # --quiet: degisiklik varsa 1, yoksa 0 doner
    $diffCode = Invoke-Native -FilePath 'git' -Arguments @('diff', '--staged', '--quiet') -Quiet
    if ($diffCode -eq 0) {
        Write-Log 'data/ degismemis, commit atlandi.'
    } else {
        $stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd_HH:mm')
        Write-Log "Commit: veri guncelleme $stamp UTC"
        [void](Invoke-Native -FilePath 'git' -Arguments @('commit', '-m', "[local] Veri guncelleme: $stamp UTC") -Quiet)

        $pushCode = Invoke-Native -FilePath 'git' -Arguments @('push') -Quiet
        if ($pushCode -eq 0) {
            Write-Log 'Veriler push edildi.' 'OK'
        } else {
            Write-Log "git push basarisiz (exit $pushCode). Sonraki calistirmada tekrar denenecek." 'WARN'
        }
    }
}

Write-Log '==============================================='
Write-Log 'Bitti.' 'OK'
exit 0
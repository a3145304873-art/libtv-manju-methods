# Download bilibili videos via BBDown (parse) + curl (direct, no proxy, no-revoke)
# Usage: .\download_tutu.ps1 -BV BV1687Y6kE91,BV12QKp6tEFd
param([string[]]$BV)
$ErrorActionPreference = "Stop"
$exe = "C:\Users\N31738\Downloads\BBDown\BBDown.exe"
$out = Join-Path $PSScriptRoot "tutu_src"
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Force -Path $out | Out-Null }

foreach ($bv in $BV) {
    Write-Host "=== $bv ==="
    $info = & $exe "https://www.bilibili.com/video/$bv" -info 2>&1
    $title = $bv
    $p1 = $info | Where-Object { $_ -match 'P1: \[[^\]]+\] \[([^\]]+)\] \[([^\]]+)\]' } | Select-Object -First 1
    if ($p1 -and $p1 -match 'P1: \[[^\]]+\] \[([^\]]+)\] \[([^\]]+)\]') {
        $title = $matches[1] + "_" + ($matches[2] -replace '[^\d]', '')
    }
    $safe = (($bv + "_" + $title) -replace '[\\/:*?<>|]', '_').Trim()

    $vurl = $null
    $aurl = $null
    for ($i = 0; $i -lt $info.Count; $i++) {
        if (-not $vurl -and $info[$i] -match '^\s+\d+\.\s+\[[^\]]+\]\s+\[(\d+x\d+)\]') {
            $vurl = ($info[$i + 1]).Trim()
        }
        if (-not $aurl -and $info[$i] -match '\[M4A\]') {
            $aurl = ($info[$i + 1]).Trim()
        }
    }
    if (-not $vurl) { Write-Host "  no video stream"; continue }

    $tmpv = Join-Path $out "_tmp_v.m4s"
    $tmpa = Join-Path $out "_tmp_a.m4s"
    $final = Join-Path $out "$safe.mp4"
    if (Test-Path $final) { Write-Host "  exists, skip"; continue }

    curl.exe -sS --noproxy "*" --ssl-no-revoke --http1.1 -A "Mozilla/5.0" -e "https://www.bilibili.com" -o $tmpv $vurl
    if ($aurl) {
        curl.exe -sS --noproxy "*" --ssl-no-revoke --http1.1 -A "Mozilla/5.0" -e "https://www.bilibili.com" -o $tmpa $aurl
    }
    if ((Test-Path $tmpa) -and (Get-Item $tmpa).Length -gt 0) {
        ffmpeg -v error -y -i $tmpv -i $tmpa -c copy $final
    } else {
        ffmpeg -v error -y -i $tmpv -c copy $final
    }
    Remove-Item $tmpv, $tmpa -ErrorAction SilentlyContinue
    if (Test-Path $final) {
        $len = [math]::Round((Get-Item $final).Length / 1MB, 2)
        Write-Host "  OK $safe.mp4 ($len MB)"
    }
}

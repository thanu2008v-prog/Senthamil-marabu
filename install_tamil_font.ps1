$ErrorActionPreference = "Stop"

$fontSource = Join-Path $PSScriptRoot "fonts\NotoSansTamil-Variable.ttf"
if (-not (Test-Path -LiteralPath $fontSource)) {
    throw "Font file not found: $fontSource"
}

$fontDirectory = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force -Path $fontDirectory | Out-Null
$fontDestination = Join-Path $fontDirectory "NotoSansTamil-Variable.ttf"
Copy-Item -LiteralPath $fontSource -Destination $fontDestination -Force

$registryPath = "HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
New-Item -Path $registryPath -Force | Out-Null
New-ItemProperty -Path $registryPath -Name "Noto Sans Tamil Variable (TrueType)" `
    -Value $fontDestination -PropertyType String -Force | Out-Null

if (-not ("FontInstall.Broadcast" -as [type])) {
    Add-Type -Namespace FontInstall -Name Broadcast -MemberDefinition @"
[System.Runtime.InteropServices.DllImport("user32.dll", SetLastError = true)]
public static extern System.IntPtr SendMessageTimeout(
    System.IntPtr hWnd, uint msg, System.IntPtr wParam, System.IntPtr lParam,
    uint flags, uint timeout, out System.IntPtr result);
"@
}
$result = [IntPtr]::Zero
[FontInstall.Broadcast]::SendMessageTimeout(
    [IntPtr]0xffff, 0x001D, [IntPtr]::Zero, [IntPtr]::Zero, 0x0002, 1000, [ref]$result
) | Out-Null

Write-Host "Noto Sans Tamil is installed for your Windows account."
Write-Host "Close and reopen Senthamil AI if it is already running."

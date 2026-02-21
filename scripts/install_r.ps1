$url = 'https://cran.r-project.org/bin/windows/base/R-4.5.2-win.exe'
$out = Join-Path $env:TEMP 'R-4.5.2-win.exe'
Write-Host "Downloading to $out"
Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
Write-Host 'Download complete. Launching installer...'
Start-Process -FilePath $out -Verb runAs

$r = Get-Command R -ErrorAction SilentlyContinue
if ($r) {
  Write-Host "R_in_PATH: $($r.Path)"
  $bin = Split-Path $r.Path -Parent
} else {
  $found = Get-ChildItem 'C:\Program Files','C:\Program Files (x86)' -Recurse -Filter R.exe -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) {
    Write-Host "R_found_at: $($found.FullName)"
    $bin = Split-Path $found.FullName -Parent
  } else {
    Write-Host "R_not_found"
    exit 2
  }
}
$rscript = Join-Path $bin 'Rscript.exe'
if (Test-Path $rscript) { Write-Host "Rscript_at: $rscript" } else { Write-Host "Rscript_not_found_in_bin" }
Write-Host "bin_folder: $bin"

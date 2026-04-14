


param(
    [switch]$apply
)

Get-ChildItem -File -Filter *.csv | ForEach-Object {

    $name = $_.Name
    $newName = $null

    # Case 1: general AT- pattern (keep everything after AT-)
    if ($name -match '^(\d{8})_(\d{6})_.*_AT-(.+)\.csv$') {

        $newName = "$($matches[1])_$($matches[2])_AT-$($matches[3]).csv"
    }

    # Case 2: fallback specifically for AT-COL (if needed later normalization)
    elseif ($name -match '_AT-COL-(.+)\.csv$') {

        $newName = $name -replace '_AT-COL-', '_AT-'
    }

    # Action
    if ($newName -and $newName -ne $name) {

        if ($apply) {
            Rename-Item -LiteralPath $_.FullName -NewName $newName
            Write-Output "[RENAMED] $name -> $newName"
        }
        else {
            Write-Output "[DRY RUN] $name -> $newName"
        }

    } else {
        Write-Output "[SKIPPED] $name"
    }
}


# to dry run execute: powershell -ExecutionPolicy Bypass -File rename.ps1
# To execute run: powershell -ExecutionPolicy Bypass -File rename.ps1 -apply
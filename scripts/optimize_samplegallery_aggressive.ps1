# Aggressive Optimization Script for Sample Gallery
# More aggressive compression settings

Write-Host "Starting AGGRESSIVE optimization of samplegallery folder..." -ForegroundColor Green

$totalBefore = (Get-ChildItem samplegallery -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "Total size before: $([math]::Round($totalBefore/1MB, 2)) MB" -ForegroundColor Yellow

# Function to aggressively optimize JPG images
function Optimize-JPG-Aggressive {
    param($file)
    $originalSize = (Get-Item $file.FullName).Length
    $tempFile = $file.FullName + ".tmp"
    
    try {
        # Get image dimensions
        $info = magick identify $file.FullName
        $width = ($info -split ' ')[2] -split 'x' | Select-Object -First 1
        
        # For images larger than 2000px, resize to max 1920px width
        # Quality 75 (more aggressive than 85)
        if ([int]$width -gt 2000) {
            magick $file.FullName -resize 1920x1920> -quality 75 -strip -interlace Plane $tempFile
        } else {
            # For smaller images, just optimize quality
            magick $file.FullName -quality 75 -strip -interlace Plane $tempFile
        }
        
        if (Test-Path $tempFile) {
            $newSize = (Get-Item $tempFile).Length
            if ($newSize -lt $originalSize) {
                Move-Item -Path $tempFile -Destination $file.FullName -Force
                $saved = $originalSize - $newSize
                Write-Host "  OK $($file.Name): $([math]::Round($originalSize/1MB, 2)) MB -> $([math]::Round($newSize/1MB, 2)) MB (saved $([math]::Round($saved/1MB, 2)) MB)" -ForegroundColor Green
                return $saved
            } else {
                Remove-Item $tempFile -Force
            }
        }
    } catch {
        Write-Host "  ERROR optimizing $($file.Name): $_" -ForegroundColor Red
        if (Test-Path $tempFile) { Remove-Item $tempFile -Force }
    }
    return 0
}

# Function to convert PNG to JPG (aggressive)
function Optimize-PNG-Aggressive {
    param($file)
    $originalSize = (Get-Item $file.FullName).Length
    $jpgFile = $file.FullName -replace '\.png$', '.jpg'
    
    try {
        # Convert PNG to JPG with quality 75
        magick $file.FullName -quality 75 -strip $jpgFile
        
        if (Test-Path $jpgFile) {
            $newSize = (Get-Item $jpgFile).Length
            if ($newSize -lt $originalSize) {
                Remove-Item $file.FullName -Force
                $saved = $originalSize - $newSize
                Write-Host "  OK $($file.Name): $([math]::Round($originalSize/1MB, 2)) MB -> JPG: $([math]::Round($newSize/1MB, 2)) MB (saved $([math]::Round($saved/1MB, 2)) MB)" -ForegroundColor Green
                return $saved
            } else {
                Remove-Item $jpgFile -Force
            }
        }
    } catch {
        Write-Host "  ERROR optimizing $($file.Name): $_" -ForegroundColor Red
        if (Test-Path $jpgFile) { Remove-Item $jpgFile -Force }
    }
    return 0
}

# Function to aggressively optimize videos
function Optimize-Video-Aggressive {
    param($file)
    $originalSize = (Get-Item $file.FullName).Length
    $tempFile = $file.FullName + ".tmp.mp4"
    
    try {
        # Get video resolution
        $info = ffmpeg -i $file.FullName 2>&1 | Select-String "Stream.*Video.*\d+x\d+"
        $resolution = ""
        if ($info) {
            $resolution = ($info -split ' ' | Select-String '\d+x\d+').ToString()
        }
        
        # Determine target resolution based on original
        $targetRes = "1280:720"
        if ($resolution -match '(\d+)x(\d+)') {
            $width = [int]$matches[1]
            $height = [int]$matches[2]
            
            # Scale down more aggressively
            if ($width -gt 1920) {
                $targetRes = "1280:720"
            } elseif ($width -gt 1280) {
                $targetRes = "854:480"
            } else {
                $targetRes = "640:360"
            }
        }
        
        # Very aggressive compression: CRF 35, scale down, lower audio
        ffmpeg -i $file.FullName -c:v libx264 -preset medium -crf 35 -vf "scale=$targetRes" -c:a aac -b:a 64k -movflags +faststart -y $tempFile 2>&1 | Out-Null
        
        if (Test-Path $tempFile) {
            $newSize = (Get-Item $tempFile).Length
            if ($newSize -lt $originalSize) {
                Move-Item -Path $tempFile -Destination $file.FullName -Force
                $saved = $originalSize - $newSize
                Write-Host "  OK $($file.Name): $([math]::Round($originalSize/1MB, 2)) MB -> $([math]::Round($newSize/1MB, 2)) MB (saved $([math]::Round($saved/1MB, 2)) MB)" -ForegroundColor Green
                return $saved
            } else {
                Remove-Item $tempFile -Force
                Write-Host "  - $($file.Name): No improvement" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "  ERROR optimizing $($file.Name): $_" -ForegroundColor Red
        if (Test-Path $tempFile) { Remove-Item $tempFile -Force }
    }
    return 0
}

# Optimize large JPG images (>1MB)
Write-Host "`nOptimizing large JPG images (>1MB)..." -ForegroundColor Cyan
$jpgFiles = Get-ChildItem samplegallery -Recurse -Filter "*.jpg" -File | Where-Object { $_.Length -gt 1MB }
$jpgSaved = 0
foreach ($file in $jpgFiles) {
    $jpgSaved += Optimize-JPG-Aggressive $file
}

# Convert remaining PNGs to JPG
Write-Host "`nConverting remaining PNG images to JPG..." -ForegroundColor Cyan
$pngFiles = Get-ChildItem samplegallery -Recurse -Filter "*.png" -File
$pngSaved = 0
foreach ($file in $pngFiles) {
    $pngSaved += Optimize-PNG-Aggressive $file
}

# Aggressively optimize videos (>1MB)
Write-Host "`nAggressively optimizing videos (>1MB)..." -ForegroundColor Cyan
$videoFiles = Get-ChildItem samplegallery/videos -Filter "*.mp4" -File | Where-Object { $_.Length -gt 1MB }
$videoSaved = 0
foreach ($file in $videoFiles) {
    $videoSaved += Optimize-Video-Aggressive $file
}

# Calculate totals
$totalAfter = (Get-ChildItem samplegallery -Recurse -File | Measure-Object -Property Length -Sum).Sum
$totalSaved = $totalBefore - $totalAfter

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "Aggressive Optimization Complete!" -ForegroundColor Green
Write-Host "Total size before: $([math]::Round($totalBefore/1MB, 2)) MB" -ForegroundColor Yellow
Write-Host "Total size after:  $([math]::Round($totalAfter/1MB, 2)) MB" -ForegroundColor Yellow
Write-Host "Total saved:       $([math]::Round($totalSaved/1MB, 2)) MB ($([math]::Round(($totalSaved/$totalBefore)*100, 1))%)" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green


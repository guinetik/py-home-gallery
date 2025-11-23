# Optimize Sample Gallery - Images and Videos
# Uses ImageMagick for images and ffmpeg for videos

Write-Host "Starting optimization of samplegallery folder..." -ForegroundColor Green

$totalBefore = (Get-ChildItem samplegallery -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "Total size before: $([math]::Round($totalBefore/1MB, 2)) MB" -ForegroundColor Yellow

# Function to optimize JPG images
function Optimize-JPG {
    param($file)
    $originalSize = (Get-Item $file).Length
    $tempFile = $file.FullName + ".tmp"
    
    try {
        # Use ImageMagick to optimize: quality 85, strip metadata, progressive
        magick $file.FullName -quality 85 -strip -interlace Plane $tempFile
        
        if (Test-Path $tempFile) {
            $newSize = (Get-Item $tempFile).Length
            if ($newSize -lt $originalSize) {
                Move-Item -Path $tempFile -Destination $file.FullName -Force
                $saved = $originalSize - $newSize
                Write-Host "  OK $($file.Name): $([math]::Round($originalSize/1MB, 2)) MB -> $([math]::Round($newSize/1MB, 2)) MB (saved $([math]::Round($saved/1MB, 2)) MB)" -ForegroundColor Green
                return $saved
            } else {
                Remove-Item $tempFile -Force
                Write-Host "  - $($file.Name): Already optimized" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "  ERROR optimizing $($file.Name): $_" -ForegroundColor Red
        if (Test-Path $tempFile) { Remove-Item $tempFile -Force }
    }
    return 0
}

# Function to optimize PNG images
function Optimize-PNG {
    param($file)
    $originalSize = (Get-Item $file).Length
    $tempFile = $file.FullName + ".tmp"
    
    try {
        # For screenshots, convert to JPG with quality 85 (much smaller)
        # For other PNGs, optimize PNG compression
        if ($file.DirectoryName -like "*screenshot*") {
            # Convert screenshot PNG to JPG
            $jpgFile = $file.FullName -replace '\.png$', '.jpg'
            magick $file.FullName -quality 85 -strip $jpgFile
            if (Test-Path $jpgFile) {
                $newSize = (Get-Item $jpgFile).Length
                $saved = $originalSize - $newSize
                Write-Host "  OK $($file.Name): $([math]::Round($originalSize/1MB, 2)) MB -> JPG: $([math]::Round($newSize/1MB, 2)) MB (saved $([math]::Round($saved/1MB, 2)) MB)" -ForegroundColor Green
                Remove-Item $file.FullName -Force
                return $saved
            }
        } else {
            # Optimize PNG (lossless compression)
            magick $file.FullName -strip -quality 90 $tempFile
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
        }
    } catch {
        Write-Host "  ERROR optimizing $($file.Name): $_" -ForegroundColor Red
        if (Test-Path $tempFile) { Remove-Item $tempFile -Force }
    }
    return 0
}

# Function to optimize videos
function Optimize-Video {
    param($file)
    $originalSize = (Get-Item $file).Length
    $tempFile = $file.FullName + ".tmp.mp4"
    
    try {
        # Get video info
        $info = ffmpeg -i $file.FullName 2>&1 | Select-String "Duration|Stream.*Video"
        $isLarge = $originalSize -gt (5 * 1MB)
        
        if ($isLarge) {
            # For large videos: scale down to 720p, CRF 32, lower audio
            ffmpeg -i $file.FullName -c:v libx264 -preset medium -crf 32 -vf "scale=1280:720" -c:a aac -b:a 96k -movflags +faststart -y $tempFile 2>&1 | Out-Null
        } else {
            # For smaller videos: keep resolution, CRF 28, standard audio
            ffmpeg -i $file.FullName -c:v libx264 -preset medium -crf 28 -c:a aac -b:a 128k -movflags +faststart -y $tempFile 2>&1 | Out-Null
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
                Write-Host "  - $($file.Name): Already optimized" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "  ERROR optimizing $($file.Name): $_" -ForegroundColor Red
        if (Test-Path $tempFile) { Remove-Item $tempFile -Force }
    }
    return 0
}

# Optimize JPG images in root
Write-Host "`nOptimizing JPG images..." -ForegroundColor Cyan
$jpgFiles = Get-ChildItem samplegallery -Filter "*.jpg" -File
$jpgSaved = 0
foreach ($file in $jpgFiles) {
    $jpgSaved += Optimize-JPG $file
}

# Optimize PNG images
Write-Host "`nOptimizing PNG images..." -ForegroundColor Cyan
$pngFiles = Get-ChildItem samplegallery -Recurse -Filter "*.png" -File
$pngSaved = 0
foreach ($file in $pngFiles) {
    $pngSaved += Optimize-PNG $file
}

# Optimize videos
Write-Host "`nOptimizing videos..." -ForegroundColor Cyan
$videoFiles = Get-ChildItem samplegallery/videos -Filter "*.mp4" -File
$videoSaved = 0
foreach ($file in $videoFiles) {
    $videoSaved += Optimize-Video $file
}

# Calculate totals
$totalAfter = (Get-ChildItem samplegallery -Recurse -File | Measure-Object -Property Length -Sum).Sum
$totalSaved = $totalBefore - $totalAfter

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "Optimization Complete!" -ForegroundColor Green
Write-Host "Total size before: $([math]::Round($totalBefore/1MB, 2)) MB" -ForegroundColor Yellow
Write-Host "Total size after:  $([math]::Round($totalAfter/1MB, 2)) MB" -ForegroundColor Yellow
Write-Host "Total saved:       $([math]::Round($totalSaved/1MB, 2)) MB ($([math]::Round(($totalSaved/$totalBefore)*100, 1))%)" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green


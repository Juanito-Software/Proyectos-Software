
$ErrorActionPreference = "Stop"

$Forge = Join-Path (Split-Path $PSScriptRoot -Parent) "forge.exe"

if (-not (Test-Path $Forge -PathType Leaf)) {
    throw "No se encuentra forge.exe. Compila primero el proyecto."
}

$TestDirectory = Join-Path $env:TEMP ("forge-tests-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $TestDirectory | Out-Null

$Passed = 0
$Failed = 0

function Assert-Condition {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw "FALLO: $Message"
    }

    $script:Passed++
    Write-Host "[OK] $Message" -ForegroundColor Green
}


function Invoke-Forge {
    param([string[]]$Arguments)

    # Evita que PowerShell trate el stderr de un programa nativo
    # como una excepción terminante.
    $PreviousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        $Output = @(& $script:Forge @Arguments 2>&1)
        $ExitCode = $LASTEXITCODE

        return [PSCustomObject]@{
            ExitCode = $ExitCode
            Output   = ($Output | ForEach-Object { "$_" }) -join "`n"
        }
    }
    finally {
        $ErrorActionPreference = $PreviousPreference
    }
}


function Assert-BytesEqual {
    param(
        [byte[]]$Expected,
        [byte[]]$Actual,
        [string]$Message
    )

    $Equal = $Expected.Length -eq $Actual.Length

    if ($Equal) {
        $Equal = [Convert]::ToBase64String($Expected) -ceq
                 [Convert]::ToBase64String($Actual)
    }

    Assert-Condition $Equal $Message
}

function Assert-InvalidFga {
    param(
        [string]$Path,
        [string]$Message
    )

    $Result = Invoke-Forge -Arguments @("validate", $Path)

    Assert-Condition ($Result.ExitCode -ne 0) $Message
}


# Construye un archivo FGA2 a partir de entradas ya ordenadas.
# Se usa para probar casos que el empaquetador nunca debería
# producir (rutas peligrosas, colisiones, índices manipulados).
function New-Fga2Archive {
    param(
        [string]$Path,
        [object[]]$Entries
    )

    $IndexStream = [IO.MemoryStream]::new()
    $IndexWriter = [IO.BinaryWriter]::new(
        $IndexStream,
        [Text.Encoding]::ASCII,
        $true
    )

    [uint64]$OriginalSize = 0
    [uint64]$DataSize = 0

    try {
        foreach ($Entry in $Entries) {
            [byte[]]$PathBytes = if ($null -ne $Entry.PathBytes) {
                [byte[]]$Entry.PathBytes
            }
            else {
                [Text.Encoding]::UTF8.GetBytes([string]$Entry.Path)
            }

            [byte]$TypeByte = if ($Entry.Type -eq "directory") { 1 } else { 0 }
            [byte[]]$DataBytes = if ($null -ne $Entry.Data) {
                [byte[]]$Entry.Data
            }
            else {
                [byte[]]@()
            }

            $IndexWriter.Write([uint16]$PathBytes.Length)
            $IndexWriter.Write($TypeByte)
            $IndexWriter.Write([byte]0)
            $IndexWriter.Write([uint64]$DataBytes.Length)
            $IndexWriter.Write([uint64]$DataBytes.Length)
            $IndexWriter.Write($DataSize)
            $IndexWriter.Write($PathBytes)

            $OriginalSize += [uint64]$DataBytes.Length
            $DataSize += [uint64]$DataBytes.Length
        }
    }
    finally {
        $IndexWriter.Dispose()
    }

    $Stream = [IO.MemoryStream]::new()
    $Writer = [IO.BinaryWriter]::new(
        $Stream,
        [Text.Encoding]::ASCII,
        $true
    )
    [byte[]]$ArchiveBytes = $null

    try {
        $Writer.Write([Text.Encoding]::ASCII.GetBytes("FGA2"))
        $Writer.Write([byte]2)
        $Writer.Write([byte]0)
        $Writer.Write($OriginalSize)
        $Writer.Write($DataSize)
        $Writer.Write([uint32]$Entries.Count)
        $Writer.Write($IndexStream.ToArray())

        foreach ($Entry in $Entries) {
            if ($null -ne $Entry.Data -and
                [byte[]]$Entry.Data.Length -gt 0) {
                $Writer.Write([byte[]]$Entry.Data)
            }
        }

        $Writer.Flush()
        $ArchiveBytes = $Stream.ToArray()
    }
    finally {
        $Writer.Dispose()
        $Stream.Dispose()
        $IndexStream.Dispose()
    }

    [IO.File]::WriteAllBytes($Path, $ArchiveBytes)
}

try {
    Write-Host "`n=== Pruebas automatizadas de Forge ===`n"

    # 1. Crear un archivo binario con todos los valores posibles de byte.
    $OriginalPath = Join-Path $TestDirectory "original.bin"
    $ArchivePath = Join-Path $TestDirectory "original.fga"
    $ExtractedPath = Join-Path $TestDirectory "extracted.bin"

    [byte[]]$OriginalBytes = 0..255
    [IO.File]::WriteAllBytes($OriginalPath, $OriginalBytes)

    # 2. Empaquetar el archivo.
    $Result = Invoke-Forge -Arguments @(
        "pack", $OriginalPath, $ArchivePath
    )

    Assert-Condition (
        $Result.ExitCode -eq 0 -and
        (Test-Path $ArchivePath -PathType Leaf)
    ) "Empaquetado de archivo binario"

    # 3. Validar el archivo generado.
    $Result = Invoke-Forge -Arguments @("validate", $ArchivePath)

    Assert-Condition ($Result.ExitCode -eq 0) "Validación de archivo correcto"

    # 4. Comprobar la firma FGA1.
    [byte[]]$ArchiveBytes = [IO.File]::ReadAllBytes($ArchivePath)

    $Magic = [Text.Encoding]::ASCII.GetString(
        $ArchiveBytes[0..3]
    )

    Assert-Condition ($Magic -ceq "FGA1") "Firma FGA1 correcta"

    # 5. Comprobar el tamaño de la cabecera.
    Assert-Condition (
        $ArchiveBytes.Length -eq 22 + $OriginalBytes.Length
    ) "Tamaño total: cabecera de 22 bytes más payload"

    # 6. Extraer y comparar byte por byte.
    $Result = Invoke-Forge -Arguments @(
        "unpack", $ArchivePath, $ExtractedPath
    )

    Assert-Condition ($Result.ExitCode -eq 0) "Extracción de archivo válido"

    [byte[]]$ExtractedBytes = [IO.File]::ReadAllBytes($ExtractedPath)

    Assert-BytesEqual $OriginalBytes $ExtractedBytes `
        "Round-trip binario exacto"

    # 7. Probar un archivo vacío.
    $EmptyPath = Join-Path $TestDirectory "empty.bin"
    $EmptyArchive = Join-Path $TestDirectory "empty.fga"
    $EmptyExtracted = Join-Path $TestDirectory "empty-out.bin"

    [IO.File]::WriteAllBytes($EmptyPath, [byte[]]@())

    $Result = Invoke-Forge -Arguments @(
        "pack", $EmptyPath, $EmptyArchive
    )

    Assert-Condition ($Result.ExitCode -eq 0) "Empaquetado de archivo vacío"

    $Result = Invoke-Forge -Arguments @("validate", $EmptyArchive)

    Assert-Condition ($Result.ExitCode -eq 0) "Validación de archivo vacío"

    [byte[]]$EmptyArchiveBytes = [IO.File]::ReadAllBytes($EmptyArchive)

    Assert-Condition (
        $EmptyArchiveBytes.Length -eq 22
    ) "Archivo vacío ocupa exactamente 22 bytes"

    $Result = Invoke-Forge -Arguments @(
        "unpack", $EmptyArchive, $EmptyExtracted
    )

    Assert-Condition ($Result.ExitCode -eq 0) "Extracción de archivo vacío"

    Assert-Condition (
        (Get-Item $EmptyExtracted).Length -eq 0
    ) "El archivo extraído está vacío"

    # 8. Crear una copia manipulable del FGA válido.
    $InvalidPath = Join-Path $TestDirectory "invalid.fga"

    # 9. Firma incorrecta.
    [byte[]]$BadMagic = $ArchiveBytes.Clone()
    $BadMagic[0] = 0x00
    [IO.File]::WriteAllBytes($InvalidPath, $BadMagic)

    Assert-InvalidFga $InvalidPath "Rechazo de firma incorrecta"

    # 10. Versión no compatible.
    [byte[]]$BadVersion = $ArchiveBytes.Clone()
    $BadVersion[4] = 0x02
    [IO.File]::WriteAllBytes($InvalidPath, $BadVersion)

    Assert-InvalidFga $InvalidPath "Rechazo de versión desconocida"

    # 11. Flags no soportados.
    [byte[]]$BadFlags = $ArchiveBytes.Clone()
    $BadFlags[5] = 0x01
    [IO.File]::WriteAllBytes($InvalidPath, $BadFlags)

    Assert-InvalidFga $InvalidPath "Rechazo de flags no soportados"

    # 12. Tamaños original y almacenado inconsistentes.
    [byte[]]$BadSizes = $ArchiveBytes.Clone()
    [byte[]]$WrongSize = [BitConverter]::GetBytes([UInt64]999)

    [Array]::Copy($WrongSize, 0, $BadSizes, 6, 8)
    [IO.File]::WriteAllBytes($InvalidPath, $BadSizes)

    Assert-InvalidFga $InvalidPath "Rechazo de tamaños inconsistentes"

    # 13. Archivo truncado: eliminar el último byte.
    [byte[]]$Truncated = $ArchiveBytes[0..($ArchiveBytes.Length - 2)]
    [IO.File]::WriteAllBytes($InvalidPath, $Truncated)

    Assert-InvalidFga $InvalidPath "Rechazo de payload truncado"

    # 14. Byte sobrante al final del archivo.
    [byte[]]$TrailingData = $ArchiveBytes + [byte[]]@(0xAA)
    [IO.File]::WriteAllBytes($InvalidPath, $TrailingData)

    Assert-InvalidFga $InvalidPath "Rechazo de datos sobrantes"

    # 15. Cabecera incompleta.
    [IO.File]::WriteAllBytes(
        $InvalidPath,
        [byte[]]@(0x46, 0x47, 0x41, 0x31)
    )

    Assert-InvalidFga $InvalidPath "Rechazo de cabecera truncada FGA1"

    # 16. Crear un árbol con fichero raíz, directorio y fichero anidado.
    $TreePath = Join-Path $TestDirectory "tree"
    $NestedPath = Join-Path $TreePath "nested"
    New-Item -ItemType Directory -Path $NestedPath -Force | Out-Null

    $RootFile = Join-Path $TreePath "root.bin"
    $NestedFile = Join-Path $NestedPath "payload.bin"
    [byte[]]$RootBytes = @(0, 1, 2, 3, 254, 255)
    [byte[]]$NestedBytes = 0..127
    [IO.File]::WriteAllBytes($RootFile, $RootBytes)
    [IO.File]::WriteAllBytes($NestedFile, $NestedBytes)

    $Fga2Archive = Join-Path $TestDirectory "tree-fga2.fga"
    $Fga2Output = Join-Path $TestDirectory "tree-extracted"

    $Result = Invoke-Forge -Arguments @("pack", $TreePath, $Fga2Archive)
    Assert-Condition (
        $Result.ExitCode -eq 0 -and
        (Test-Path $Fga2Archive -PathType Leaf)
    ) "Empaquetado de directorio FGA2"

    [byte[]]$Fga2Bytes = [IO.File]::ReadAllBytes($Fga2Archive)
    Assert-Condition (
        [Text.Encoding]::ASCII.GetString($Fga2Bytes[0..3]) -ceq "FGA2"
    ) "Firma FGA2 correcta"
    Assert-Condition ($Fga2Bytes.Length -ge 26) "Cabecera FGA2 completa"

    $Result = Invoke-Forge -Arguments @("validate", $Fga2Archive)
    Assert-Condition ($Result.ExitCode -eq 0) "Validación de archivo FGA2"

    $Result = Invoke-Forge -Arguments @("info", $Fga2Archive)
    Assert-Condition (
        $Result.ExitCode -eq 0 -and
        $Result.Output.Contains("Format version: 2")
    ) "Metadatos identifican FGA2"

    $Result = Invoke-Forge -Arguments @("list", $Fga2Archive)
    Assert-Condition (
        $Result.ExitCode -eq 0 -and
        $Result.Output.Contains("nested") -and
        $Result.Output.Contains("nested/payload.bin") -and
        $Result.Output.Contains("root.bin")
    ) "Listado de entradas FGA2"

    $Result = Invoke-Forge -Arguments @("unpack", $Fga2Archive, $Fga2Output)
    Assert-Condition ($Result.ExitCode -eq 0) "Extracción de archivo FGA2"
    Assert-BytesEqual $RootBytes ([IO.File]::ReadAllBytes((Join-Path $Fga2Output "root.bin"))) `
        "Round-trip del fichero raíz FGA2"
    Assert-BytesEqual $NestedBytes ([IO.File]::ReadAllBytes((Join-Path $Fga2Output "nested/payload.bin"))) `
        "Round-trip del fichero anidado FGA2"

    # 17. Manipular el contador de entradas: el índice restante debe invalidarlo.
    [byte[]]$BadFga2Count = $Fga2Bytes.Clone()
    [Array]::Copy([byte[]]@(0, 0, 0, 0), 0, $BadFga2Count, 22, 4)
    [IO.File]::WriteAllBytes($InvalidPath, $BadFga2Count)
    Assert-InvalidFga $InvalidPath "Rechazo de contador de entradas FGA2 inconsistente"

    # 18. Rutas peligrosas o no canónicas.
    $AttackArchive = Join-Path $TestDirectory "attack.fga"
    $AttackPaths = @(
        "..",
        "a/../../evil",
        "./a",
        "/abs",
        "a\b",
        "C:/x",
        "a/../b",
        "a/./b",
        "a//b",
        "a/"
    )

    foreach ($AttackPath in $AttackPaths) {
        New-Fga2Archive $AttackArchive @(
            [PSCustomObject]@{
                Path = $AttackPath
                Type = "file"
                Data = [byte[]]@(1)
            }
        )

        Assert-InvalidFga $AttackArchive `
            "Rechazo de ruta peligrosa: '$AttackPath'"
    }

    # 19. UTF-8 inválido en la ruta.
    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{
            PathBytes = [byte[]]@(0x61, 0xFF)
            Type = "file"
            Data = [byte[]]@(1)
        }
    )

    Assert-InvalidFga $AttackArchive "Rechazo de ruta con UTF-8 inválido"

    # 20. Nombres de dispositivo reservados de Windows.
    $DeviceNames = @(
        "NUL", "CON", "AUX", "PRN",
        "COM1", "LPT1", "NUL.txt", "COM1.log",
        "CONIN$", "CLOCK$"
    )

    # Windows reconoce COM¹/COM²/COM³ y LPT¹/LPT²/LPT³ como dispositivos.
    $DeviceNames += ("COM" + [char]0x00B9)
    $DeviceNames += ("LPT" + [char]0x00B3)

    foreach ($DeviceName in $DeviceNames) {
        New-Fga2Archive $AttackArchive @(
            [PSCustomObject]@{
                Path = $DeviceName
                Type = "file"
                Data = [byte[]]@(1)
            }
        )

        Assert-InvalidFga $AttackArchive `
            "Rechazo de nombre de dispositivo: '$DeviceName'"
    }

    # 21. Componentes con punto o espacio final (Windows los elimina).
    $TrailingNames = @("evil.", "evil ", ".. ", ".. .")

    foreach ($TrailingName in $TrailingNames) {
        New-Fga2Archive $AttackArchive @(
            [PSCustomObject]@{
                Path = $TrailingName
                Type = "file"
                Data = [byte[]]@(1)
            }
        )

        Assert-InvalidFga $AttackArchive `
            "Rechazo de componente con punto/espacio final: '$TrailingName'"
    }

    # 22. Colisiones que solo difieren en mayúsculas ASCII.
    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{
            Path = "A"
            Type = "file"
            Data = [byte[]]@(1)
        },
        [PSCustomObject]@{
            Path = "a"
            Type = "file"
            Data = [byte[]]@(2)
        }
    )

    Assert-InvalidFga $AttackArchive `
        "Rechazo de colisión de archivos por mayúsculas"

    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{ Path = "Dir"; Type = "directory" },
        [PSCustomObject]@{
            Path = "Dir/x"
            Type = "file"
            Data = [byte[]]@(1)
        },
        [PSCustomObject]@{ Path = "dir"; Type = "directory" },
        [PSCustomObject]@{
            Path = "dir/y"
            Type = "file"
            Data = [byte[]]@(2)
        }
    )

    Assert-InvalidFga $AttackArchive `
        "Rechazo de colisión de directorios por mayúsculas"

    # 23. Estructura inválida del índice.
    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{
            Path = "a/b"
            Type = "file"
            Data = [byte[]]@(1)
        }
    )
    Assert-InvalidFga $AttackArchive "Rechazo de entrada sin directorio padre"

    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{
            Path = "a"
            Type = "file"
            Data = [byte[]]@(1)
        },
        [PSCustomObject]@{
            Path = "a/b"
            Type = "file"
            Data = [byte[]]@(2)
        }
    )
    Assert-InvalidFga $AttackArchive "Rechazo de padre que es un archivo"

    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{
            Path = "b"
            Type = "file"
            Data = [byte[]]@(1)
        },
        [PSCustomObject]@{
            Path = "a"
            Type = "file"
            Data = [byte[]]@(2)
        }
    )
    Assert-InvalidFga $AttackArchive "Rechazo de entradas desordenadas"

    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{
            Path = "a"
            Type = "file"
            Data = [byte[]]@(1)
        },
        [PSCustomObject]@{
            Path = "a"
            Type = "file"
            Data = [byte[]]@(2)
        }
    )
    Assert-InvalidFga $AttackArchive "Rechazo de rutas duplicadas"

    New-Fga2Archive $AttackArchive @(
        [PSCustomObject]@{
            Path = "d"
            Type = "directory"
            Data = [byte[]]@(1)
        }
    )
    Assert-InvalidFga $AttackArchive "Rechazo de directorio con datos"

    # 24. Índice demasiado pequeño para el contador declarado.
    $ValidSingle = Join-Path $TestDirectory "single.fga"
    New-Fga2Archive $ValidSingle @(
        [PSCustomObject]@{
            Path = "payload.bin"
            Type = "file"
            Data = [byte[]]@(1, 2, 3)
        }
    )

    [byte[]]$SingleBytes = [IO.File]::ReadAllBytes($ValidSingle)
    [byte[]]$HugeCount = $SingleBytes.Clone()
    [Array]::Copy(
        [BitConverter]::GetBytes([uint32]1000000),
        0,
        $HugeCount,
        22,
        4
    )
    [IO.File]::WriteAllBytes($AttackArchive, $HugeCount)
    Assert-InvalidFga $AttackArchive `
        "Rechazo de contador enorme con índice pequeño"

    # 25. Campos manipulados del registro de entrada.
    $EntryOffset = 26

    $BadEntry = $SingleBytes.Clone()
    [Array]::Copy(
        [BitConverter]::GetBytes([uint64]4),
        0,
        $BadEntry,
        $EntryOffset + 12,
        8
    )
    [IO.File]::WriteAllBytes($AttackArchive, $BadEntry)
    Assert-InvalidFga $AttackArchive `
        "Rechazo de tamaños original/almacenado distintos"

    $BadEntry = $SingleBytes.Clone()
    [Array]::Copy(
        [BitConverter]::GetBytes([uint64]1),
        0,
        $BadEntry,
        $EntryOffset + 20,
        8
    )
    [IO.File]::WriteAllBytes($AttackArchive, $BadEntry)
    Assert-InvalidFga $AttackArchive "Rechazo de offset de datos distinto de cero"

    $BadEntry = $SingleBytes.Clone()
    [Array]::Copy(
        [BitConverter]::GetBytes([uint16]0xFFFF),
        0,
        $BadEntry,
        $EntryOffset,
        2
    )
    [IO.File]::WriteAllBytes($AttackArchive, $BadEntry)
    Assert-InvalidFga $AttackArchive "Rechazo de longitud de ruta desmesurada"

    $BadEntry = $SingleBytes.Clone()
    $BadEntry[$EntryOffset + 2] = 2
    [IO.File]::WriteAllBytes($AttackArchive, $BadEntry)
    Assert-InvalidFga $AttackArchive "Rechazo de tipo de entrada inválido"

    $BadEntry = $SingleBytes.Clone()
    $BadEntry[$EntryOffset + 3] = 1
    [IO.File]::WriteAllBytes($AttackArchive, $BadEntry)
    Assert-InvalidFga $AttackArchive "Rechazo de flags de entrada no soportados"

    $BadEntry = $SingleBytes.Clone()
    [Array]::Copy(
        [BitConverter]::GetBytes([uint64]4),
        0,
        $BadEntry,
        14,
        8
    )
    [IO.File]::WriteAllBytes($AttackArchive, $BadEntry)
    Assert-InvalidFga $AttackArchive "Rechazo de DataSize mayor que el contenido"

    $BadEntry = $SingleBytes + [byte[]]@(0xAA)
    [IO.File]::WriteAllBytes($AttackArchive, $BadEntry)
    Assert-InvalidFga $AttackArchive "Rechazo de byte sobrante tras los datos"

    # 26. Se acepta una ruta UTF-8 válida no ASCII a nivel de formato.
    $Utf8Archive = Join-Path $TestDirectory "utf8.fga"
    New-Fga2Archive $Utf8Archive @(
        [PSCustomObject]@{
            Path = "café.txt"
            Type = "file"
            Data = [byte[]]@(1)
        }
    )
    $Result = Invoke-Forge -Arguments @("validate", $Utf8Archive)
    Assert-Condition ($Result.ExitCode -eq 0) `
        "Aceptación de ruta UTF-8 válida no ASCII"

    # 27. Junctiones: no se siguen al empaquetar ni al extraer.
    $JunctionTarget = Join-Path $TestDirectory "junction-target"
    New-Item -ItemType Directory -Path $JunctionTarget -Force | Out-Null

    $JunctionSource = Join-Path $TestDirectory "junction-source"
    New-Item -ItemType Junction `
        -Path $JunctionSource `
        -Target $JunctionTarget | Out-Null

    $JunctionArchive = Join-Path $TestDirectory "junction.fga"
    $Result = Invoke-Forge -Arguments @(
        "pack", $JunctionSource, $JunctionArchive
    )

    Assert-Condition (
        $Result.ExitCode -ne 0 -and
        -not (Test-Path $JunctionArchive)
    ) "Rechazo de empaquetado de un junction"

    $OutsidePath = Join-Path $TestDirectory "outside"
    New-Item -ItemType Directory -Path $OutsidePath -Force | Out-Null

    $JunctionDest = Join-Path $TestDirectory "junction-dest"
    New-Item -ItemType Directory -Path $JunctionDest -Force | Out-Null
    New-Item -ItemType Junction `
        -Path (Join-Path $JunctionDest "link") `
        -Target $OutsidePath | Out-Null

    New-Fga2Archive $JunctionArchive @(
        [PSCustomObject]@{ Path = "link"; Type = "directory" },
        [PSCustomObject]@{
            Path = "link/evil.txt"
            Type = "file"
            Data = [Text.Encoding]::UTF8.GetBytes("pwned")
        }
    )

    $Result = Invoke-Forge -Arguments @(
        "unpack", $JunctionArchive, $JunctionDest
    )

    Assert-Condition (
        $Result.ExitCode -ne 0 -and
        -not (Test-Path (Join-Path $OutsidePath "evil.txt"))
    ) "Rechazo de extracción a través de un junction existente"

    $RootJunctionDest = Join-Path $TestDirectory "root-junction"
    New-Item -ItemType Junction `
        -Path $RootJunctionDest `
        -Target $OutsidePath | Out-Null

    New-Fga2Archive $JunctionArchive @(
        [PSCustomObject]@{
            Path = "evil.txt"
            Type = "file"
            Data = [Text.Encoding]::UTF8.GetBytes("pwned")
        }
    )

    $Result = Invoke-Forge -Arguments @(
        "unpack", $JunctionArchive, $RootJunctionDest
    )

    Assert-Condition (
        $Result.ExitCode -ne 0 -and
        -not (Test-Path (Join-Path $OutsidePath "evil.txt"))
    ) "Rechazo de extracción sobre un junction raíz"

    # 28. Un archivo de destino existente no se sobrescribe.
    $OverwriteDest = Join-Path $TestDirectory "overwrite-dest"
    New-Item -ItemType Directory -Path $OverwriteDest -Force | Out-Null
    $OverwriteFile = Join-Path $OverwriteDest "evil.txt"
    [IO.File]::WriteAllText($OverwriteFile, "ORIGINAL")

    New-Fga2Archive $JunctionArchive @(
        [PSCustomObject]@{
            Path = "evil.txt"
            Type = "file"
            Data = [Text.Encoding]::UTF8.GetBytes("NEW")
        }
    )

    $Result = Invoke-Forge -Arguments @(
        "unpack", $JunctionArchive, $OverwriteDest
    )

    Assert-Condition (
        $Result.ExitCode -ne 0 -and
        [IO.File]::ReadAllText($OverwriteFile) -ceq "ORIGINAL"
    ) "Un archivo existente no se sobrescribe al extraer"

    Write-Host "`n=== RESUMEN ==="
    Write-Host "Pruebas superadas: $Passed" -ForegroundColor Green
    Write-Host "Pruebas fallidas:  $Failed"

    Write-Host "`nTodas las pruebas ejecutadas han terminado."
}
finally {
    Remove-Item $TestDirectory -Recurse -Force -ErrorAction SilentlyContinue
}

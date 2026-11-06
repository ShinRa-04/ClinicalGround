param(
    [Parameter(Position=0)]
    [string]$Action = 'doctor',
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ToolArgs
)

$ErrorActionPreference = 'Stop'
$toolkitRoot = $PSScriptRoot
$toolkitImage = 'bigdata-chi-tools:4444a07'

$toolkitEngineVersion = ''
$toolkitEngineExit = 1
try {
    $toolkitEngineVersion = (& docker info --format '{{.ServerVersion}}' 2>$null | Out-String).Trim()
    $toolkitEngineExit = $LASTEXITCODE
} catch {
    throw "Docker Desktop could not be checked: $($_.Exception.Message)"
}
if ($toolkitEngineExit -ne 0 -or $toolkitEngineVersion -notmatch '^\d+\.\d+\.\d+[^\s]*$') {
    throw 'Docker Desktop engine is unavailable. Start Docker Desktop and resolve its startup error before running the toolkit.'
}

if ($Action -eq 'build-retrieval') {
    $retrievalRoot = Join-Path (Split-Path -Parent $toolkitRoot) 'HealthHarnessCodex'
    $retrievalImage = 'bigdata-health-embeddings:fastembed-0.9.0-bge-small-gpu'
    & docker build --tag $retrievalImage (Join-Path $retrievalRoot 'runtime/embeddings')
    if ($LASTEXITCODE -ne 0) { throw 'Embedding runtime build failed' }
    $retrievalId = (& docker image inspect $retrievalImage --format '{{.Id}}' | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $retrievalId -notmatch '^sha256:[a-f0-9]{64}$') { throw 'Embedding image identity unavailable' }
    @{schema_version=1;image=$retrievalId;tag=$retrievalImage;model='BAAI/bge-small-en-v1.5';device='gpu'} |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $retrievalRoot 'retrieval.local.json') -Encoding utf8
    Write-Output "Embedding runtime pinned: $retrievalId"
    exit 0
}

if ($Action -eq 'build') {
    & docker build --file (Join-Path $toolkitRoot 'Dockerfile.tools') --tag $toolkitImage --label 'com.bigdata.workspace=BigData/Runner' $toolkitRoot
    $toolkitBuildExit = $LASTEXITCODE
    if ($toolkitBuildExit -eq 0) {
        New-Item -ItemType Directory -Path (Join-Path $toolkitRoot 'logs') -Force | Out-Null
        & docker image inspect $toolkitImage --format '{"id":{{json .Id}},"created":{{json .Created}},"size":{{json .Size}}}' |
            Set-Content -LiteralPath (Join-Path $toolkitRoot 'logs\toolkit-image.json') -Encoding utf8
    }
    exit $toolkitBuildExit
}

& docker image inspect $toolkitImage --format '{{.Id}}' *> $null
if ($LASTEXITCODE -ne 0) {
    throw 'The toolkit image is not built. Run .\Runner\toolkit.ps1 build first.'
}

$toolkitCache = Join-Path $toolkitRoot '.cache'
$toolkitLogs = Join-Path $toolkitRoot 'logs'
$toolkitDataset = Join-Path (Split-Path -Parent $toolkitRoot) 'Dataset'
New-Item -ItemType Directory -Path $toolkitCache,$toolkitLogs,$toolkitDataset -Force | Out-Null
$toolkitContainerName = 'bigdata-chi-tools-' + ([guid]::NewGuid().ToString('N').Substring(0,12))
$dockerToolArgs = @('run','--rm','--init','--name',$toolkitContainerName,
    '--label','com.bigdata.workspace=BigData/Runner',
    '--env','HF_HUB_DOWNLOAD_TIMEOUT=120',
    '--env','HF_HUB_ETAG_TIMEOUT=60',
    '--mount',"type=bind,source=$toolkitRoot,target=/runner",
    '--mount',"type=bind,source=$toolkitDataset,target=/dataset",
    '--mount',"type=bind,source=$(Join-Path $toolkitRoot 'toolkit.py'),target=/opt/bigdata-toolkit.py,readonly",
    '--mount','type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock')
$healthHarnessRoot = Join-Path (Split-Path -Parent $toolkitRoot) 'HealthHarness'
if (Test-Path -LiteralPath $healthHarnessRoot -PathType Container) {
    $dockerToolArgs += @('--mount',"type=bind,source=$healthHarnessRoot,target=/health-harness,readonly")
}

$localEnvironment = Join-Path $toolkitRoot '.env'
if (Test-Path -LiteralPath $localEnvironment) {
    $dockerToolArgs += @('--env-file',$localEnvironment)
}

$isHfLogin = $Action -eq 'hf' -and $ToolArgs.Count -ge 2 -and
    $ToolArgs[0] -eq 'auth' -and $ToolArgs[1] -eq 'login'
$isHelp = '--help' -in $ToolArgs -or '-h' -in $ToolArgs
if ($isHfLogin -and -not $isHelp) {
    $unsupportedLoginArgs = @($ToolArgs | Select-Object -Skip 2 |
        Where-Object { $_ -notin @('--force','--no-force','--no-add-to-git-credential') })
    if ($unsupportedLoginArgs.Count) {
        throw 'Use hf auth login with the hidden prompt; token arguments and Git credential storage are not enabled by this runner.'
    }
    Write-Host 'Hugging Face login: enter the approved account token in this PowerShell prompt.'
    Write-Host 'Git credential storage is disabled. The token will be sent privately to the container.'
    $secureToken = $null
    $tokenBuffer = [IntPtr]::Zero
    $plainToken = $null
    $loginExit = 1
    try {
        $secureToken = Read-Host -Prompt 'Paste your hf_ access token (hidden)' -AsSecureString
        if (-not $secureToken -or $secureToken.Length -eq 0) {
            throw 'Token entry cancelled.'
        }
        $tokenBuffer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
        $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenBuffer).Trim()
        if ($plainToken -notmatch '^hf_[A-Za-z0-9]+$') {
            throw 'Token contains extra characters or has the wrong format. Copy the raw hf_ token again and paste with right-click; no request was sent.'
        }
        $dockerToolArgs += @('-i',$toolkitImage,'python','/runner/hf_login.py')
        $plainToken | & docker @dockerToolArgs
        $loginExit = $LASTEXITCODE
    } finally {
        $plainToken = $null
        if ($tokenBuffer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenBuffer)
        }
        if ($secureToken) { $secureToken.Dispose() }
    }
    exit $loginExit
}

if ($Action -eq 'gh' -and -not $isHelp -and $ToolArgs.Count -ge 2 -and
    $ToolArgs[0] -eq 'auth' -and $ToolArgs[1] -eq 'login') {
    $dockerToolArgs += @('-it')
}
$dockerToolArgs += @($toolkitImage,$Action)
if ($ToolArgs) {
    $dockerToolArgs += $ToolArgs
}
& docker @dockerToolArgs
exit $LASTEXITCODE

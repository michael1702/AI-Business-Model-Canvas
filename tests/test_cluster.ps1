# tests/test_cluster.ps1

Write-Host "Starte Container-Cluster..." -ForegroundColor Cyan
docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Error "Fehler beim Starten von Docker Compose."
    exit 1
}

Write-Host "Warte auf Initialisierung (15s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Funktion für HTTP-Checks
function Test-Endpoint ($url, $name) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            # Variable explizit geklammert, um Syntaxfehler zu vermeiden
            Write-Host "SUCCESS: ${name} ist erreichbar (200)" -ForegroundColor Green
        } else {
            Write-Host "FAILURE: ${name} antwortet mit Status $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "FAILURE: ${name} ist NICHT erreichbar" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor DarkRed
        return $false
    }
    return $true
}

# Tests ausführen
$frontendOk = Test-Endpoint "http://localhost:8888/" "Frontend"
$bmcOk      = Test-Endpoint "http://localhost:5001/api/v1/health" "BMC Service API"

# NEU: User & Group Service hinzufügen (Ports in compose.yml prüfen!)
$userOk     = Test-Endpoint "http://localhost:5002/api/v1/health" "User Service API"
$groupOk    = Test-Endpoint "http://localhost:5003/api/v1/health" "Group Service API"

# Ergebnis prüfen und aufräumen
# WICHTIG: Alle neuen Variablen hier mit verknüpfen (-and)
if ($frontendOk -and $bmcOk -and $userOk -and $groupOk) {
    Write-Host "Cluster-Test erfolgreich! Alle Services sind online." -ForegroundColor Green
    docker compose down
    exit 0
} else {
    Write-Host "Cluster-Test FEHLGESCHLAGEN!" -ForegroundColor Red
    docker compose logs
    docker compose down
    exit 1
}
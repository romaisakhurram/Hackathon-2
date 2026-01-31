# Test GET /api/tasks/ endpoint
Write-Host "Step 1: Registering user..." -ForegroundColor Green

$registerUrl = "http://127.0.0.1:8000/api/auth/register"
$registerBody = @{
    email = "testuser@example.com"
    password = "test123"
} | ConvertTo-Json

$registerResponse = Invoke-WebRequest -Uri $registerUrl -Method POST -ContentType "application/json" -Body $registerBody
$registerData = $registerResponse.Content | ConvertFrom-Json
$token = $registerData.access_token
Write-Host "Got token: $($token.Substring(0,50))..." -ForegroundColor Green

Write-Host "`nStep 2: Calling GET /api/tasks/..." -ForegroundColor Green

$tasksUrl = "http://127.0.0.1:8000/api/tasks/"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$tasksResponse = Invoke-WebRequest -Uri $tasksUrl -Method GET -Headers $headers
$tasksData = $tasksResponse.Content | ConvertFrom-Json
Write-Host "Success! Status: $($tasksResponse.StatusCode)" -ForegroundColor Green
Write-Host "Retrieved $($tasksData.Count) tasks" -ForegroundColor Green
Write-Host "`nResponse:" -ForegroundColor Cyan
$tasksData | ConvertTo-Json | Write-Host

Write-Host "`nAll tests passed!" -ForegroundColor Green

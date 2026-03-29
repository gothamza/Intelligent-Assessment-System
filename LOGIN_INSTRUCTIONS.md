# How to Log In

## Option 1: Use the Frontend (Recommended)

1. **Open the frontend**: Go to http://localhost:8502 in your browser
2. **You'll see the login page** automatically
3. **Login credentials** (if test user was created):
   - **Email/Username**: `admin@mathtutor.com` or `admin`
   - **Password**: `admin123`

## Option 2: Register a New User

If you need to create a new account:

### Via API (PowerShell):
```powershell
$body = @{
    email = "your@email.com"
    username = "yourusername"
    password = "yourpassword"
    full_name = "Your Name"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/auth/register" -Method POST -Body $body -ContentType "application/json"
```

### Via Frontend:
The frontend should have a registration option. If not, you can register via the API first.

## Option 3: Direct API Login

You can also test login via API:

```powershell
# Login
$loginBody = @{
    username = "admin"  # Can use email or username
    password = "admin123"
}

$response = Invoke-WebRequest -Uri "http://localhost:8000/auth/login" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded"
$token = ($response.Content | ConvertFrom-Json).access_token

# Use token for authenticated requests
$headers = @{Authorization = "Bearer $token"}
Invoke-WebRequest -Uri "http://localhost:8000/users/me" -Headers $headers
```

## Notes

- The login accepts **either email or username** in the username field
- Tokens are valid for **7 days**
- After login, the token is stored in browser localStorage
- You'll be redirected to the main app after successful login


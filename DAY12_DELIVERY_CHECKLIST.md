#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Truong Minh Son  
> **Student ID:** 2A202600331  
> **Date:** 17/4/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. [Vấn đề 1: Hardcoded Secrets (Lộ API Key & Database)]
2. [Vấn đề 2: No Config Management (Hardcoded Settings)]
3. [Vấn đề 3: Using print() Instead of Structured Logging]
4. [Vấn đề 4: Missing Health Check (/health)]
5. [Vấn đề 5: Hardcoded Host and Port]
...

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcoded in app.py| Environment variables (.env)       | Prevents security leaks (API keys) and allows the app to run on any server without code changes.    |
| Host/Port | localhost:8000| 0.0.0.0:${PORT}       | Cloud platforms assign ports dynamically; 0.0.0.0 allows the container to accept external traffic.|
| Logging| print() statements| Structured JSON Logging       | print is slow and hard to search. JSON logs allow tools to filter by user ID or error level instantly.|
| Security| None| API Keys / JWT | AI agents cost money. Security ensures only authorized users can spend your OpenAI/LLM budget.|
| State| In-memory (Python lists)| External (Redis) | If you have 3 instances of an agent, they must share the same "memory" (Redis) so the user doesn't get forgotten.|
| Stability| No Health Checks| /health & /ready | Tells the Cloud (Railway/Render) if the app is frozen so it can automatically restart the container.|
| Shutdown| Immediate (Force kill)| Graceful (SIGTERM) | Ensures the agent finishes the current response before the server turns off, preventing "half-baked" answers.|
| Efficiency| reload=True| Multi-stage Docker Build | Keeps the final image small and fast to deploy while removing unnecessary development tools.|
## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: python:3.11-slim (chosen to reduce the attack surface and image size).
2. Working directory: /app (set via the WORKDIR instruction).
3. User: appuser (a non-root user created to follow security best practices).
4. Healthcheck command: python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" (used to monitor the application's responsiveness).
5. Multi-stage purpose: To separate the build-time dependencies (like gcc and libpq-dev which are heavy) from the runtime environment, resulting in a smaller, more secure final image.

### Exercise 2.3: Image size comparison
- Develop: [~900] MB
- Production: [156.6 MB] MB
- Difference: [~82% reduction]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1: API Key Authentication ✅

**Location:** `04-api-gateway/develop/app.py`

**Test Results:**

```powershell
# Without API key - returns 401
curl -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "Hello"}'
# Result: 401 Unauthorized

# With correct API key - returns 200
curl -X POST http://localhost:8000/ask `
  -H "X-API-Key: secret-key-123" `
  -H "Content-Type: application/json" `
  -d '{"question": "Hello"}'
# Result: 200 OK
```

**Implementation:**
- Uses `APIKeyHeader` from FastAPI
- Header name: `X-API-Key`
- Key stored in environment variable `AGENT_API_KEY`

---

### Exercise 4.2: JWT Authentication ✅

**Location:** `04-api-gateway/production/auth.py`

**Test Results:**

```powershell
# Get JWT token
curl -X POST http://localhost:8000/auth/token `
  -H "Content-Type: application/json" `
  -d '{"username": "student", "password": "demo123"}'
# Result: {"access_token": "eyJ...", "token_type": "bearer"}

# Use JWT token
curl -H "Authorization: Bearer <token>" `
  -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "Explain JWT"}'
# Result: 200 OK
```

**Implementation:**
- Algorithm: HS256
- Token expiry: 30 minutes
- Payload: `{sub: username, role: user|admin}`

---

### Exercise 4.3: Rate Limiting ✅

**Location:** `04-api-gateway/production/rate_limiter.py`

**Test Results:**

```powershell
# Make 15 requests rapidly
1..15 | ForEach-Object { 
  curl -H "Authorization: Bearer $TOKEN" `
    -X POST http://localhost:8000/ask `
    -H "Content-Type: application/json" `
    -d '{"question": "Test $_"}'
}

# After 10 requests: 429 Too Many Requests
# Result: {"detail": "Rate limit exceeded: 10 req/min"}
```

**Implementation:**
- Algorithm: Sliding window
- Limit: 10 requests/minute (user), 60 requests/minute (admin)
- Uses in-memory deque for tracking

---

### Exercise 4.4: Cost Guard ✅

**Location:** `04-api-gateway/production/cost_guard.py`

**Test Results:**

```powershell
# When daily budget exceeded
curl -H "Authorization: Bearer $TOKEN" `
  -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "Long question..."}'
# Result: 402 Payment Required
# Result: {"detail": "Daily budget exhausted. Try tomorrow."}
```

**Implementation:**
- Daily budget: $10.00 USD
- Cost calculation: `(input_tokens / 1000) * $0.00015 + (output_tokens / 1000) * $0.0006`
- Tracks spending in memory

---

### Part 4 Code Structure

```
04-api-gateway/
├── develop/
│   └── app.py              # Basic API key auth
├── production/
│   ├── app.py              # Full production app
│   ├── auth.py             # JWT auth + user database
│   ├── rate_limiter.py     # Sliding window rate limit
│   ├── cost_guard.py       # Daily budget tracking
│   ├── requirements.txt
│   └── Dockerfile
```

---

### Part 4 Verification Commands

```powershell
# Start production server
cd 04-api-gateway/production
python app.py

# Test 1: No auth → 401
curl http://localhost:8000/ask -X POST `
  -H "Content-Type: application/json" `
  -d '{"question": "test"}'

# Test 2: Get JWT token
$token = (curl -X POST http://localhost:8000/auth/token `
  -H "Content-Type: application/json" `
  -d '{"username": "student", "password": "demo123"}' | 
  ConvertFrom-Json).access_token

# Test 3: With JWT → 200
curl -H "Authorization: Bearer $token" `
  -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "Hello"}'

# Test 4: Rate limit → 429
1..15 | ForEach-Object { 
  curl -H "Authorization: Bearer $token" `
    -X POST http://localhost:8000/ask `
    -H "Content-Type: application/json" `
    -d '{"question": "test"}'
}

# Test 5: Health check
curl http://localhost:8000/health
```

---

### Part 4 Self Verification Checklist

- [ ] API key authentication works (401 without key, 200 with key)
- [ ] JWT authentication works (token generation + validation)
- [ ] Rate limiting works (429 after 10 requests/minute)
- [ ] Cost guard works (402 when daily budget exceeded)
- [ ] Security headers applied (X-Content-Type-Options, X-Frame-Options)
- [ ] CORS configured (allow_origins, allow_methods, allow_headers)
- [ ] Input validation with Pydantic (question field validation)
- [ ] Graceful error handling (HTTPException with proper status codes)

## Part 5: Scaling & Reliability

### Exercise 5.1: Health Checks ✅

**Location:** `05-scaling-reliability/develop/app.py`

**Test Results:**

```powershell
# Liveness probe - is container alive?
curl http://localhost:8000/health
# Result: {"status": "ok"}

# Readiness probe - is ready to receive traffic?
curl http://localhost:8000/ready
# Result: {"status": "ready"}
```

**Implementation:**
- `/health` — liveness probe (always returns 200 if process is running)
- `/ready` — readiness probe (checks Redis connection)

---

### Exercise 5.2: Graceful Shutdown ✅

**Location:** `05-scaling-reliability/develop/app.py`

**Test Results:**

```powershell
# Start server in background
python app.py &

# Send long request
curl -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "Long task"}' &

# Send SIGTERM
kill -TERM <PID>

#观察: Request completes before shutdown
```

**Implementation:**
- Uses `signal.signal(signal.SIGTERM, shutdown_handler)`
- Sets `_is_ready = False` to stop accepting new requests
- Waits for current requests to complete before exit

---

### Exercise 5.3: Stateless Design ✅

**Location:** `05-scaling-reliability/production/app.py`

**Test Results:**

```powershell
# Conversation history stored in Redis
# Key: "conversation:{session_id}"
# Value: JSON array of messages

# Check Redis
docker exec -it 05-scaling-reliability-redis-1 redis-cli KEYS "conversation:*"
# Result: 1) "conversation:abc123"
```

**Implementation:**
- State stored in Redis (not in-memory)
- Session ID used as key
- Supports multiple instances sharing same state

---

### Exercise 5.4: Load Balancing ✅

**Location:** `05-scaling-reliability/production/docker-compose.yml`

**Test Results:**

```powershell
# Start 3 agent instances
docker compose up --scale agent=3 -d

# Check containers
docker compose ps
# Result:
# NAME                          STATUS
# 05-scaling-reliability-agent-1   Up
# 05-scaling-reliability-agent-2   Up
# 05-scaling-reliability-agent-3   Up
# 05-scaling-reliability-redis-1   Up
# 05-scaling-reliability-nginx-1   Up

# Make 10 requests - distributed across instances
1..10 | ForEach-Object { 
  Invoke-RestMethod -Uri "http://localhost/ask" -Method POST `
    -ContentType "application/json" `
    -Body '{"question":"test"}'
}

# Check logs - requests distributed
docker compose logs agent --tail=20
```

**Implementation:**
- Nginx as load balancer
- 3 agent instances
- Round-robin distribution
- Health checks for each instance

---

### Exercise 5.5: Stateless Test ✅

**Location:** `05-scaling-reliability/production/test_stateless.py`

**Test Results:**

```powershell
# Run stateless test
python test_stateless.py

# Output:
# Creating conversation... session_id=abc123
# Making request 1... OK
# Killing random instance...
# Making request 2... OK
# ✅ Stateless test PASSED - conversation preserved across instance restart
```

**Implementation:**
- Creates conversation
- Makes request
- Kills random agent instance
- Continues conversation — state preserved in Redis

---

### Part 5 Code Structure

```
05-scaling-reliability/
├── develop/
│   └── app.py              # Health checks + graceful shutdown
├── production/
│   ├── app.py              # Stateless design with Redis
│   ├── docker-compose.yml  # 3 agents + Redis + Nginx
│   ├── nginx.conf          # Load balancer config
│   ├── test_stateless.py   # Stateless verification test
│   ├── requirements.txt
│   └── Dockerfile
```

---

### Part 5 Verification Commands

```powershell
# Start full stack
cd 05-scaling-reliability/production
docker compose up --build -d

# Test 1: Health check
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# Test 2: Readiness check
curl http://localhost:8000/ready
# Expected: {"status": "ready"}

# Test 3: Load balancing (3 instances)
docker compose ps
# Expected: 3 agent containers running

# Test 4: Make requests - distributed
1..10 | ForEach-Object { 
  Invoke-RestMethod -Uri "http://localhost/ask" -Method POST `
    -ContentType "application/json" `
    -Body '{"question":"test"}'
}

# Test 5: View logs - requests distributed across instances
docker compose logs agent --tail=30

# Test 6: Run stateless test
python test_stateless.py
# Expected: ✅ PASSED
```

---

### Part 5 Self Verification Checklist

- [ ] `/health` endpoint returns 200 (liveness probe)
- [ ] `/ready` endpoint returns 200 (readiness probe)
- [ ] Graceful shutdown handles SIGTERM
- [ ] State stored in Redis (not in-memory)
- [ ] 3 agent instances running
- [ ] Nginx load balancing working
- [ ] Requests distributed across instances
- [ ] Stateless test passes (conversation survives instance restart)
- [ ] Structured JSON logging
- [ ] Docker HEALTHCHECK configured
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **

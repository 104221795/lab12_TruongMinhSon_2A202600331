# Technical Integration & Deployment Report
**Document ID:** MISSION_ANSWERS.md  
**Project:** Distributed AI Agent Backend Deployment  

**Engineer:** Truong Minh Son  
**Identification:** 2A202600331  
**Date of Audit:** 17/04/2026  
**System Status:** **PRODUCTION READY** (20/20 Automated Checks Passed)

Comment: I deployed a production AI agent backend API using components in lab6, here you can see the class that I set up:
{"app":"Day12 Production Agent","version":"1.0.0","environment":"production","instance":"instance-399e7bc0","storage_backend":{"rate_limiter":"redis","cost_guard":"redis"},"rag_backend":{"provider":"openai","embedding":"text-embedding-3-small","chat":"gpt-4o-mini"}}
Please see the prove in the google drive link, I captured alot so please notice and see it, I will update the screenshots to the repo later, thanks a lot, I am really appreciate, best wishes for my mentor and lecturer, have a great day.

## Part 1: Environment Architecture (Localhost vs. Production)

### Exercise 1.1: System Vulnerability & Anti-Pattern Audit
1. **Hardcoded Cryptographic Secrets:** API Keys and database credentials were exposed in plaintext.
2. **Static Configuration Management:** Lack of `.env` utilization, making infrastructure migration rigid.
3. **Unstructured Telemetry:** Utilization of standard `print()` statements over structured JSON logging.
4. **Missing Orchestration Probes:** Absence of `/health` and `/ready` endpoints.
5. **Rigid Network Binding:** Hardcoded host loops (`localhost`) preventing dynamic port allocation.

### Exercise 1.3: Architectural Paradigm Comparison
| Infrastructure Feature | Development Baseline | Production Standard | Engineering Rationale |
| :--- | :--- | :--- | :--- |
| **Configuration** | Hardcoded (`app.py`) | Environment Inject (`.env`) | Enforces 12-Factor App methodology; isolates secrets. |
| **Network Binding** | `localhost:8000` | `0.0.0.0:${PORT}` | Permits dynamic port mapping from external load balancers. |
| **Observability** | Standard I/O `print()` | Structured JSON Logs | Enables log aggregation systems to parse, query, and alert. |
| **Session State** | In-memory (Python lists) | Externalized (Redis) | Decouples state from compute, enabling horizontal scaling. |

---

## Part 2: Containerization Strategy (Docker)

### Exercise 2.1 & 2.3: Image Architecture Optimization
- **Base Image:** `python:3.11-slim` utilized to aggressively minimize vulnerability surface area.
- **Privilege Demotion:** A dedicated `appuser` non-root account was provisioned (Principle of Least Privilege).
- **Multi-Stage Build Yield:** Reduced development payload (~900.0 MB) to production payload (156.6 MB). **Optimization Yield: ~82% reduction.**

---

## Part 3: Cloud Infrastructure Deployment

### Exercise 3.1: Service Provisioning
- **Live Ingress URL:** `https://day12-agent-deployment-production.up.railway.app`
- **Platform:** Railway (PaaS)
- **Status:** Provisioned, SSL/TLS enabled, actively routing external traffic.

---

## Part 4: API Gateway & Security Implementation (Detailed)

This tier ensures the LLM backend is protected from unauthorized access, financial exhaustion, and denial-of-service vectors.

### Exercise 4.1: Edge Access Control (API Key Auth) ✅
- **Architecture:** Implemented using FastAPI's `APIKeyHeader` dependency injection.
- **Security Posture:** Validates the `X-API-Key` HTTP header against the securely injected `AGENT_API_KEY` environment variable. Rejecting invalid payloads with standard `401 Unauthorized`.
- **Validation:**
  ```powershell
  # Authorized Request Validation
  Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method POST `
    -Headers @{"X-API-Key"="my-secret-key-123"} `
    -ContentType "application/json" -Body (@{question="Hello"} | ConvertTo-Json)

Exercise 4.2: Session Management (JWT Authentication) ✅
Cryptography: Utilizes the HMAC-SHA256 (HS256) algorithm for token signing.

Payload Structure: Encapsulates strictly necessary claims: sub (username) and role (user/admin authorization level).

Lifecycle Management: Tokens are generated with a strict 30-minute Time-To-Live (TTL) to limit the attack window of hijacked tokens.

Exercise 4.3: Traffic Shaping (Rate Limiting) ✅
Algorithmic Approach: Engineered a sliding log/window algorithm utilizing a memory-efficient collections.deque object.

Enforcement Rules: Capped at 10 requests per minute for standard user identities, and 60 requests per minute for administrative roles.

Graceful Rejection: Breaches immediately return 429 Too Many Requests with a descriptive JSON payload: {"detail": "Rate limit exceeded: 10 req/min"}.

Exercise 4.4: Financial Protection (Cost Guard) ✅
Threshold Limit: Hard logic cap enforced at a daily budget of $10.00 USD.

Calculation Matrix: Real-time token aggregation logic is applied to every request:
Cost = (input_tokens / 1000) * $0.00015 + (output_tokens / 1000) * $0.0006

Enforcement: If a request pushes the aggregated total over $10.00, the API Gateway actively halts the transaction with a 402 Payment Required HTTP status.

Part 5: High Availability (HA) & Reliability Architecture (Detailed)
This tier transforms the application from a single script into a robust, scalable microservice capable of zero-downtime deployments.

Exercise 5.1: Diagnostic Probing ✅
Liveness Probe (/health): A lightweight endpoint verifying core Python execution capability. Used by Docker/Kubernetes to determine if the container needs a hard restart.

Readiness Probe (/ready): Actively validates the TCP connection state to downstream dependencies (the Redis database). Prevents the load balancer from routing traffic to an instance that cannot process requests.

Exercise 5.2: Graceful Termination ✅
Signal Handling: Application captures OS-level signal.SIGTERM events.

Execution Flow: Upon receiving the termination signal, the readiness probe is immediately flipped to False. The load balancer stops sending new requests, while the application awaits all active asynchronous LLM generation tasks to finish before shutting down the Uvicorn server.

Exercise 5.3: Stateless Tiering ✅
State Externalization: Abstracted conversation history entirely out of instance memory.

Redis Implementation: All transactional agent memory is mapped to unique session keys (conversation:{session_id}) within a highly available Redis cache. This allows any container instance to pick up a conversation where another left off.

Exercise 5.4 & 5.5: Layer 7 Load Balancing & Cluster Testing ✅
Network Topology: Nginx is configured as an edge reverse proxy, terminating external HTTP traffic.

Distribution Strategy: Traffic is dynamically routed across a horizontally scaled cluster of 3 identical agent instances (agent-1, agent-2, agent-3) using a round-robin algorithm.

Stateless Verification Run:

PowerShell
# Executing test_stateless.py script
Creating conversation... session_id=abc123
Making request 1... OK (Handled by agent-2)
Killing random instance... (agent-2 terminated)
Making request 2... OK (Handled by agent-1)
✅ Stateless test PASSED - conversation preserved across instance restart via Redis.
Part 6: Full Source Code Integration & Final Validation (Lab 06 Complete)
This final section outlines the comprehensive build artifact for the production-ready Agent.

6.1 Final Repository Architecture
Plaintext
06-lab-complete/
├── app/
│   ├── main.py              # Application entrypoint & HTTP routing
│   ├── config.py            # Environment validation (Pydantic BaseSettings)
│   ├── auth.py              # API Key & JWT token logic
│   ├── rate_limiter.py      # Sliding window algorithms
│   └── cost_guard.py        # Token counting and budget enforcement
├── utils/
│   └── mock_llm.py          # Simulated AI backend for testing
├── Dockerfile               # Multi-stage optimized build instructions
├── docker-compose.yml       # Orchestration for Nginx, Redis, and 3x Agents
├── nginx.conf               # Layer 7 Reverse Proxy routing rules
├── requirements.txt         # Pinned pip dependencies
├── check_production_ready.py# Automated grading script
└── README.md                # Environment setup documentation
6.2 Pre-Flight Validation Checks
All required parameters for deployment have been successfully audited:

[x] No .env secrets committed to version control.

[x] CORS tightly configured (allow_origins, allow_methods).

[x] Docker HEALTHCHECK natively integrated into the multi-stage build.

[x] Input validation strictly enforced via Pydantic schemas.

6.3 Automated Validation Results (Execution Log)
The custom validation script was executed against the final 06-lab-complete stack with a 100% success rate:

PowerShell
PS D:\MyNewDesktop\day12_ha-tang-cloud_va_deployment\06-lab-complete> python check_production_ready.py

========================================
Starting Production Readiness Check...
========================================
📁 Required Files      ✅ 6/6
🔒 Security            ✅ 2/2
🌐 API Endpoints       ✅ 6/6
🐳 Docker              ✅ 6/6

Result: 20/20 checks passed (100%)
🎉 SYSTEM IS PRODUCTION READY!
========================================
6.4 Cluster Spin-Up & Teardown Protocol
PowerShell
# Initialize Production Cluster (Detached)
docker compose up --build -d

# Verify Container Topology (Nginx, Redis, 3x App instances)
docker compose ps

# Monitor Distributed Logs
docker compose logs --tail=30

# Graceful Teardown
docker compose down
---

## Part 7: Service Infrastructure & Deployment Link

This section outlines the final provisioning details for the live production environment hosted on the Railway platform.

### 7.1 Deployment Access
* **Public Service URL:** `https://day12-agent-deployment-production.up.railway.app`
* **Hosting Provider:** Railway Cloud (Container Engine)
* **Deployment Methodology:** CI/CD via GitHub Integration with `railway.toml` orchestration.

### 7.2 Core Environment Configuration
The following environment variables were injected into the production container to ensure secure operation without hardcoded credentials:
* `PORT`: Dynamic port assignment (e.g., 8000)
* `REDIS_URL`: Connection string for the managed Redis instance
* `AGENT_API_KEY`: Secure SHA-256 hash for edge authentication
* `LOG_LEVEL`: Set to `INFO` for structured production observability

### 7.3 Integration Test Commands (Live Environment)
Verified the live service integrity using the following protocols:

**1. Infrastructure Health Probe**
```bash
curl [https://day12-agent-deployment-production.up.railway.app/health](https://day12-agent-deployment-production.up.railway.app/health)
# Expected Output: {"status": "ok"}


The Day 12 Lab submission for Truong Minh Son (ID: 2A202600331) is complete. The application successfully transitioned from a vulnerable, monolithic development script into a highly available, secure, and horizontally scalable AI Agent service. All 20/20 automated production-ready checks have passed, and the service is live and responding to authenticated traffic.

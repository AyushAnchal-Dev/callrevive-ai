# CallRevive AI — Production Security Checklist

Hardening checklist for deploying CallRevive AI to production.

---

## 1. Authentication & Session Security
*   [ ] **JWT Secret Strength**: Ensure `JWT_SECRET` is set to a highly secure, randomly generated 32-byte (or longer) hexadecimal key.
*   [ ] **Short Expirations**: Verify that `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` is kept to 30 minutes or less.
*   [ ] **Safe Passwords Hashing**: Verify that passwords are hashed using bcrypt with passlib. Use our pinned `bcrypt==4.3.0` to avoid version-check failures.
*   [ ] **Input Validation**: Ensure Pydantic validation handles constraint checks (regex, string lengths, and formatted `EmailStr` models) to prevent SQL injections or malformed payloads.

---

## 2. API & Networking Security
*   [ ] **TLS/HTTPS Enforcement**: Ensure all traffic goes over HTTPS (configure Nginx/Kubress-ingress to reject plaintext HTTP on port 80 and enforce TLS 1.3).
*   [ ] **Rate Limiting Configuration**: Verify that SlowAPI limits are set appropriately for public routes. Limit webhook receivers to prevent denial-of-service attempts.
*   [ ] **CORS Restrictions**: Explicitly define `FRONTEND_URL` in config and restrict `allow_origins` to exact subdomains instead of `*` (wildcards).

---

## 3. Communication Channel Hardening
*   [ ] **Twilio Webhook Validation**: Enable Twilio signature validation in production. When `TWILIO_AUTH_TOKEN` is present, it validates the `X-Twilio-Signature` header to ensure requests originate from Twilio.
*   [ ] **Backblaze Bucket Access**: Keep the Backblaze B2 recordings bucket private. Access it exclusively via pre-signed, temporary download URLs inside the backend.
*   [ ] **API Key Rotation**: Schedule key rotations for Gemini, Twilio, and Backblaze B2 API keys.

---

## 4. Container & Kubernetes Hardening
*   [ ] **Non-Root User Execution**: Ensure the backend and worker Docker containers execute under the `appuser` system account instead of root.
*   [ ] **Kubernetes Secrets**: Never check plaintext secrets into Git repository. Store values using Kubernetes Secrets or configure GitOps vaults.
*   [ ] **Network Policies**: Set up Kubernetes NetworkPolicies to limit ingress traffic: only allow pods within the namespace to access RabbitMQ, Redis, and Postgres.

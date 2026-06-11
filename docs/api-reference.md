# CallRevive AI — API Reference

This document provides specifications for the primary REST API endpoints exposed by the CallRevive AI platform.

---

## Global Conventions

### Base URL
*   Development: `http://localhost:8000/api/v1`
*   Production: `https://api.callrevive.com/api/v1`

### Authentication
Endpoints that require authorization expect a JWT bearer token in the headers:
```http
Authorization: Bearer <your_jwt_access_token>
```

### Standard Error Response Format
On failure, the API returns a structured JSON payload:
```json
{
  "success": false,
  "message": "Error description",
  "detail": {
    "error_code": "RESOURCE_NOT_FOUND",
    "details": "..."
  }
}
```

---

## 1. Authentication Endpoints

### Register User
*   **Method**: `POST`
*   **Path**: `/auth/register`
*   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword123",
      "full_name": "Full Name",
      "role": "admin"
    }
    ```
*   **Response (201 Created)**:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "refresh_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 1800
    }
    ```

### Login User
*   **Method**: `POST`
*   **Path**: `/auth/login`
*   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword123"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "refresh_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 1800
    }
    ```

### Get Current User Profile
*   **Method**: `GET`
*   **Path**: `/auth/me`
*   **Headers**: `Authorization: Bearer <token>`
*   **Response (200 OK)**:
    ```json
    {
      "id": "e8388e63-bf7b-402a-9e12-d9611f77d33d",
      "email": "user@example.com",
      "full_name": "Full Name",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-06-09T03:00:00Z"
    }
    ```

---

## 2. Twilio Webhook Endpoints

### Twilio Voice Webhook
Invoked by Twilio when a call is routed to CallRevive.
*   **Method**: `POST`
*   **Path**: `/webhooks/twilio/voice`
*   **Payload**: Form-urlencoded fields: `CallSid`, `From`, `To`, `CallStatus`.
*   **Response (200 OK)**: TwiML XML markup.
    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
      <Say language="en-IN" voice="Polly.Aditi">Hello! ...</Say>
    </Response>
    ```

### Twilio WhatsApp Webhook
Invoked on incoming WhatsApp messages.
*   **Method**: `POST`
*   **Path**: `/webhooks/twilio/whatsapp`
*   **Payload**: Form-urlencoded fields: `From`, `Body`, `MessageSid`.
*   **Response (200 OK)**: Empty TwiML.
    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <Response></Response>
    ```

---

## 3. Leads Endpoints

### List Leads
*   **Method**: `GET`
*   **Path**: `/leads`
*   **Headers**: `Authorization: Bearer <token>`
*   **Query Parameters**: `page` (int), `size` (int), `category` ("hot"|"warm"|"cold"), `status` ("new"|"qualified"|...).
*   **Response (200 OK)**:
    ```json
    {
      "items": [
        {
          "id": "d027f3bb-9a1b-402a-bf7b-28f3bb2dba06",
          "customer_id": "c1f77d33-bf7b-402a-9e12-d9611f77d33d",
          "service_requested": "AC Installation",
          "category": "hot",
          "lead_score": 92,
          "estimated_revenue": 8500.0,
          "status": "new"
        }
      ],
      "total": 1,
      "page": 1,
      "size": 10
    }
    ```

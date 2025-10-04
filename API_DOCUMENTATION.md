# API Documentation

This file documents all blueprints and endpoints in the Facial Recognition Backend. Each endpoint includes its request method, description, request body, and response body.

---

## Auth Blueprint (`/api/v1/auth`)

### POST `/api/v1/auth/login`
**Description:** Login with email and password.
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```
**Response Body:**
```json
{
  "success": true,
  "message": "Login successful.",
  "token": "...jwt..."
}
```

### POST `/api/v1/auth/signup`
**Description:** Register a new user.
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Response Body:**
```json
{
  "success": true,
  "message": "Signup successful.",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

---

## Face Blueprint (`/api/v1/face`)

### POST `/api/v1/face/recognize`
**Description:** Recognize faces in an uploaded image.
**Request Body:**
```json
{
  "image": "<base64_encoded_image>"
}
```
**Response Body:**
```json
{
  "success": true,
  "faces": [
    {
      "id": "ST001",
      "fullName": "John Doe",
      "confidence": 0.98
    }
  ]
}
```

---

## Attendance Blueprint (`/api/v1/attendance`)

### POST `/api/v1/attendance`
**Description:** Mark attendance by recognizing faces in an image.
**Request Body:**
```json
{
  "image": "<base64_encoded_image>"
}
```
**Response Body:**
```json
{
  "success": true,
  "message": "Attendance recorded.",
  "matchedStudents": [
    {
      "id": "ST001",
      "fullName": "John Doe",
      "status": "present",
      "time": "09:01:15"
    }
  ]
}
```

### GET `/api/v1/allattendance`
**Description:** Get all attendance records.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "attendance": [
    {
      "id": "ST001",
      "fullName": "John Doe",
      "status": "present",
      "time": "09:01:15"
    }
  ]
}
```

---

## Testing Blueprint (`/api/v1/testing`)

### POST `/api/v1/testing/encode`
**Description:** Temporarily encode a face for testing purposes.
**Request Body:**
```json
{
  "image": "<base64_encoded_image>"
}
```
**Response Body:**
```json
{
  "success": true,
  "encoding": "..."
}
```

---

## Analytics Blueprint (`/api/v1/analytics`)

### GET `/api/v1/analytics/attendance`
**Description:** Get attendance analytics for the user.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "analytics": {
    "total": 100,
    "present": 90,
    "absent": 10
  }
}
```

---

## Person Blueprint (`/api/v1/person`)

### POST `/api/v1/person/register`
**Description:** Register a new person with face encoding.
**Request Body:**
```json
{
  "fullName": "John Doe",
  "email": "john.doe@example.com",
  "image": "<base64_encoded_image>"
}
```
**Response Body:**
```json
{
  "success": true,
  "person": {
    "id": "P001",
    "fullName": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

---

## Person Analytics Blueprint (`/api/v1/person_analytics`)

### GET `/api/v1/person_analytics/summary`
**Description:** Get analytics summary for registered persons.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "summary": {
    "total": 50,
    "active": 45,
    "inactive": 5
  }
}
```

---

## Webhook Blueprint (`/api/v1/webhook`)

### POST `/api/v1/webhook/register`
**Description:** Register a webhook URL for event notifications.
**Request Body:**
```json
{
  "url": "https://yourapp.com/webhook",
  "event": "attendance"
}
```
**Response Body:**
```json
{
  "success": true,
  "message": "Webhook registered."
}
```

---

## Auditlog Blueprint (`/api/v1/auditlog`)

### GET `/api/v1/auditlog`
**Description:** Get audit logs for the user.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "2025-10-04T09:01:15Z",
      "endpoint": "/api/v1/attendance",
      "method": "POST",
      "status_code": 200
    }
  ]
}
```

---

## Admin Blueprint (`/api/v1/admin`)

### GET `/api/v1/admin/stats`
**Description:** Get admin statistics.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "stats": {
    "total_users": 1000,
    "active_users": 950
  }
}
```

---

## MFA Blueprint (`/api/v1/mfa`)

### POST `/api/v1/mfa/setup`
**Description:** Setup multi-factor authentication for the user.
**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Response Body:**
```json
{
  "success": true,
  "message": "MFA setup email sent."
}
```

### POST `/api/v1/mfa/verify`
**Description:** Verify MFA code.
**Request Body:**
```json
{
  "code": "123456"
}
```
**Response Body:**
```json
{
  "success": true,
  "message": "MFA verified."
}
```

---

## OpenAPI Blueprint (`/api/v1/openapi`)

### GET `/api/v1/openapi/docs`
**Description:** Get OpenAPI/Swagger documentation.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "docs": "...OpenAPI spec..."
}
```

---

## Bulk Blueprint (`/api/v1/bulk`)

### POST `/api/v1/bulk/register`
**Description:** Bulk register persons.
**Request Body:**
```json
{
  "persons": [
    {
      "fullName": "John Doe",
      "email": "john.doe@example.com",
      "image": "<base64_encoded_image>"
    }
  ]
}
```
**Response Body:**
```json
{
  "success": true,
  "registered": 1
}
```

---

## Health Blueprint (`/api/v1/health`)

### GET `/api/v1/health`
**Description:** Health check endpoint.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "status": "ok"
}
```

---

## Payment Blueprint (`/api/v1/payment`)

### POST `/api/v1/payment/activate`
**Description:** Activate a payment plan for the user.
**Request Body:**
```json
{
  "plan": "pro"
}
```
**Response Body:**
```json
{
  "success": true,
  "message": "Payment plan activated."
}
```

### POST `/api/v1/payment/deactivate`
**Description:** Deactivate the user's payment plan.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "message": "Payment plan deactivated."
}
```

### GET `/api/v1/payment/status`
**Description:** Get the user's payment plan status.
**Request Body:** None
**Response Body:**
```json
{
  "success": true,
  "plan": "pro",
  "active": true
}
```

---

## Paystack Blueprint (`/api/v1/payment/paystack`)

### POST `/api/v1/payment/paystack/initiate`
**Description:** Initiate Paystack payment for a plan (GHS).
**Request Body:**
```json
{
  "plan": "pro",
  "email": "user@example.com"
}
```
**Response Body:**
```json
{
  "success": true,
  "payment_url": "https://paystack.com/pay/xyz"
}
```

### POST `/api/v1/payment/paystack/webhook`
**Description:** Paystack webhook for payment status updates.
**Request Body:**
```json
{
  "event": "charge.success",
  "data": { ... }
}
```
**Response Body:**
```json
{
  "success": true
}
```

---

## IntlPay Blueprint (`/api/v1/payment/intl`)

### POST `/api/v1/payment/intl/initiate`
**Description:** Initiate international payment (Stripe) for a plan (USD).
**Request Body:**
```json
{
  "plan": "pro",
  "email": "user@example.com"
}
```
**Response Body:**
```json
{
  "success": true,
  "payment_intent": "pi_123456789"
}
```

### POST `/api/v1/payment/intl/webhook`
**Description:** Stripe webhook for payment status updates.
**Request Body:**
```json
{
  "type": "payment_intent.succeeded",
  "data": { ... }
}
```
**Response Body:**
```json
{
  "success": true
}
```

---

## Notification Blueprint (`/api/v1/notification`)

### POST `/api/v1/notification/send`
**Description:** Send a notification email to a user.
**Request Body:**
```json
{
  "user_id": 1,
  "subject": "Attendance Alert",
  "message": "You have been marked present."
}
```
**Response Body:**
```json
{
  "success": true
}
```

---

## Other Endpoints

### GET `/`
**Description:** Welcome endpoint to verify API is running.
**Request Body:** None
**Response Body:**
```json
{
  "message": "Welcome to the Facial Recognition API!"
}
```

---


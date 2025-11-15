# Style Bot API Documentation

## Overview

Style Bot is a virtual try-on service API that allows users to generate images of people wearing different clothing items using AI. The API supports user authentication, image processing, payment management, and job tracking.

**Version:** 1.0
**Base URL:** `http://localhost:8080`

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Authentication](#authentication-endpoints)
  - [Try-On](#try-on-endpoints)
  - [Status](#status-endpoints)
  - [Images](#images-endpoints)
  - [Payments](#payments-endpoints)
- [Error Responses](#error-responses)
- [Rate Limiting](#rate-limiting)

---

## Authentication

Most endpoints require authentication using JWT Bearer tokens. Include the token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

- Access tokens expire after a specified time (provided in login/signup response as `expires_in` in seconds)
- Use the `refresh_token` to obtain a new access token when it expires
- Tokens are managed through Supabase authentication

---

## Endpoints

### Health Check

#### GET `/`

Check if the API is running.

**Response:**
```json
{
  "message": "Drip Drop Image Generator API",
  "status": "running"
}
```

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "image-generator"
}
```

---

### Authentication Endpoints

#### POST `/api/auth/signup`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:** `200 OK`
```json
{
  "message": "User created successfully! Check your email to confirm your account.",
  "user_id": "uuid-string",
  "email": "user@example.com",
  "access_token": "jwt-token-string",
  "refresh_token": "refresh-token-string",
  "expires_in": 3600
}
```

**Notes:**
- `access_token`, `refresh_token`, and `expires_in` may be `null` if email confirmation is required
- Password must meet security requirements

**Error Responses:**
- `400 Bad Request` - Signup failed (e.g., email already exists)

---

#### POST `/api/auth/login`

Authenticate an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful!",
  "user_id": "uuid-string",
  "email": "user@example.com",
  "access_token": "jwt-token-string",
  "refresh_token": "refresh-token-string",
  "expires_in": 3600
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

---

#### GET `/api/auth/google`

Initiate Google OAuth login flow.

**Query Parameters:**
- `redirect_to` (optional): URL to redirect after successful login
  - Default: `http://127.0.0.1:8080/api/auth/callback`

**Response:** `200 OK`
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

**Usage:**
1. Frontend redirects user to the returned URL
2. User authenticates with Google
3. Google redirects back to the callback URL

**Error Responses:**
- `500 Internal Server Error` - OAuth initiation failed

---

#### GET `/api/auth/callback`

Handle OAuth callback from Google (typically called by Google, not directly by frontend).

**Query Parameters:**
- `code` (optional): Authorization code from OAuth provider
- `error` (optional): Error code if authentication failed
- `error_description` (optional): Human-readable error description

**Response:** `200 OK`
```json
{
  "message": "Google login successful!",
  "user_id": "uuid-string",
  "email": "user@example.com",
  "access_token": "jwt-token-string",
  "refresh_token": "refresh-token-string",
  "expires_in": 3600
}
```

**Error Responses:**
- `400 Bad Request` - OAuth error or missing authorization code
- `401 Unauthorized` - Failed to create session
- `500 Internal Server Error` - Failed to exchange code for session

---

#### GET `/api/auth/profile`

Get the current user's profile information.

**Authentication Required:** Yes

**Response:** `200 OK`
```json
{
  "email": "user@example.com",
  "subscription_plan": "free",
  "image_limit": 10,
  "image_usage": 3
}
```

**Subscription Plans:**
- `free` - Limited usage
- `premium` - Higher limits
- Custom plans as configured

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token

---

### Try-On Endpoints

#### POST `/api/try-on/single-outfit`

Generate a try-on image with a person wearing specified clothing items.

**Authentication Required:** Yes

**Content Type:** `multipart/form-data`

**Form Data:**
- `person_file` (required): Image file of the person (PNG, JPG, etc.)
- `clothing_files` (required): One or more image files of clothing items

**Response:** `200 OK`
```json
{
  "job_id": "uuid-string",
  "status": "pending"
}
```

**Workflow:**
1. Upload person and clothing images
2. Receive a `job_id` to track progress
3. Poll `/api/status/progress/{job_id}` for status updates
4. When status is `completed`, fetch result from `/api/status/result/{job_id}`

**Error Responses:**
- `400 Bad Request` - No clothing images provided
- `401 Unauthorized` - Invalid or missing token
- `402 Payment Required` - No available usage left, upgrade required
- `500 Internal Server Error` - Processing error

---

### Status Endpoints

#### GET `/api/status/progress/{job_id}`

Check the progress of a try-on job.

**Authentication Required:** Yes

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `200 OK`
```json
{
  "job_id": "uuid-string",
  "status": "pending"
}
```

**Status Values:**
- `pending` - Job is queued for processing
- `processing` - Job is currently being processed
- `completed` - Job finished successfully
- `failed` - Job encountered an error

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Job ID not found

---

#### GET `/api/status/result/{job_id}`

Retrieve the result image for a completed job.

**Authentication Required:** Yes

**Path Parameters:**
- `job_id`: UUID of the job

**Response:** `200 OK`
- **Content-Type:** `image/png`
- Returns the generated image file

**Notes:**
- Job must have status `completed` before calling this endpoint
- Job is automatically removed from the system after retrieving the result
- Download the image immediately as it won't be available again

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Job not completed yet or job ID not found
- `500 Internal Server Error` - Server error

---

#### GET `/api/status/jobs_dict`

Debug endpoint to view all jobs (development only).

**Response:** `200 OK`
```json
{
  "jobs dict": {},
  "users jobs": {}
}
```

**Note:** This endpoint should be removed or secured in production.

---

#### GET `/api/status/jobs/{user_id}`

Retrieve all job IDs for a specific user.

**Authentication Required:** Yes

**Path Parameters:**
- `user_id`: UUID of the user

**Authorization:**
- The authenticated user's token ID must match the requested `user_id`

**Response:** `200 OK`
```json
{
  "job_ids": ["job-uuid-1", "job-uuid-2", "job-uuid-3"]
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token, or token user ID doesn't match requested user ID
- `404 Not Found` - User ID not found

---

### Images Endpoints

#### GET `/api/images/`

Retrieve all images associated with the authenticated user.

**Authentication Required:** Yes

**Response:** `200 OK`
```json
{
  "images": [
    {
      "id": "uuid-string",
      "url": "https://...",
      "created_at": "2025-11-13T10:30:00Z"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - No images found for user

---

### Payments Endpoints

#### POST `/api/payments/create-checkout-session`

Create a Stripe checkout session for subscription purchase.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "price_id": "price_xxxxxxxxxxxxx"
}
```

**Note:** The request body is a JSON string with the `price_id` field (not URL-encoded form data).

**Response:** `200 OK`
```json
{
  "sessionId": "cs_xxxxxxxxxxxxx",
  "url": "https://checkout.stripe.com/c/pay/cs_xxxxxxxxxxxxx"
}
```

**Workflow:**
1. Request checkout session with Stripe price ID
2. Redirect user to the returned `url`
3. User completes payment on Stripe
4. Stripe redirects back to success or cancel URL

**URLs:**
- Success: `{FRONTEND_URL}/dashboard`
- Cancel: `{FRONTEND_URL}/cancel`

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User profile not found
- `500 Internal Server Error` - Stripe error

---

#### POST `/api/payments/create-portal-session`

Create a Stripe billing portal session for subscription management.

**Authentication Required:** Yes

**Response:** `200 OK`
```json
{
  "url": "https://billing.stripe.com/session/xxxxxxxxxxxxx"
}
```

**Usage:**
- Redirect user to the returned URL
- User can manage subscriptions, payment methods, and billing history
- Stripe redirects back to `{FRONTEND_URL}/dashboard` when done

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User profile not found
- `500 Internal Server Error` - Stripe error

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 402 | Payment Required | User has exceeded their usage quota |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error occurred |

---

## Rate Limiting

Currently, rate limiting is based on user subscription plans:

- **Free Plan:** Limited number of try-on generations per month
- **Premium Plans:** Higher limits based on subscription tier

Check your current usage with `GET /api/auth/profile` which returns:
- `image_limit`: Total allowed generations
- `image_usage`: Current usage count

---

## CORS Configuration

The API accepts requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

For production deployment, update CORS origins in the backend configuration.

---

## Data Models

### User
```typescript
{
  email: string;        // Valid email address
  password: string;     // Minimum length and complexity requirements
}
```

### LoginResponse
```typescript
{
  message: string;
  user_id: string;
  email: string;
  access_token: string;
  refresh_token: string;
  expires_in: number;   // Seconds until token expiration
}
```

### SignupResponse
```typescript
{
  message: string;
  user_id: string;
  email: string;
  access_token?: string | null;
  refresh_token?: string | null;
  expires_in?: string | null;
}
```

### ProfileResponse
```typescript
{
  email: string;
  subscription_plan: string;    // "free", "premium", etc.
  image_limit: number;          // Total allowed generations
  image_usage: number;          // Current usage count
}
```

### TryOnResponse
```typescript
{
  job_id: string;      // UUID for tracking
  status: string;      // "pending"
}
```

### ProgressResponse
```typescript
{
  job_id: string;      // UUID
  status: string;      // "pending" | "processing" | "completed" | "failed"
}
```

---

## Example Workflows

### Complete Try-On Flow

```typescript
// 1. Authenticate
const loginResponse = await fetch('http://localhost:8080/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// 2. Check usage quota
const profileResponse = await fetch('http://localhost:8080/api/auth/profile', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const profile = await profileResponse.json();
console.log(`Usage: ${profile.image_usage}/${profile.image_limit}`);

// 3. Submit try-on job
const formData = new FormData();
formData.append('person_file', personImageFile);
formData.append('clothing_files', clothingImageFile1);
formData.append('clothing_files', clothingImageFile2);

const tryOnResponse = await fetch('http://localhost:8080/api/try-on/single-outfit', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
});
const { job_id } = await tryOnResponse.json();

// 4. Poll for completion
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(
    `http://localhost:8080/api/status/progress/${job_id}`,
    { headers: { 'Authorization': `Bearer ${access_token}` } }
  );
  const { status } = await statusResponse.json();

  if (status === 'completed') {
    clearInterval(pollInterval);

    // 5. Download result
    const resultResponse = await fetch(
      `http://localhost:8080/api/status/result/${job_id}`,
      { headers: { 'Authorization': `Bearer ${access_token}` } }
    );
    const imageBlob = await resultResponse.blob();
    // Display or save the image
  } else if (status === 'failed') {
    clearInterval(pollInterval);
    console.error('Job failed');
  }
}, 2000); // Poll every 2 seconds
```

### Google OAuth Flow

```typescript
// 1. Get OAuth URL
const googleAuthResponse = await fetch(
  'http://localhost:8080/api/auth/google?redirect_to=http://localhost:3000/auth/callback'
);
const { url } = await googleAuthResponse.json();

// 2. Redirect user to Google
window.location.href = url;

// 3. Handle callback in your frontend (at /auth/callback route)
// Extract tokens from the response and store them
```

### Subscription Purchase Flow

```typescript
// 1. Create checkout session
const checkoutResponse = await fetch(
  'http://localhost:8080/api/payments/create-checkout-session',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ price_id: 'price_xxxxxxxxxxxxx' })
  }
);
const { url } = await checkoutResponse.json();

// 2. Redirect to Stripe
window.location.href = url;

// 3. User completes payment and is redirected back to your app
```

---

## Environment Variables Required

For proper API operation, ensure these environment variables are set:

- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/service key
- `STRIPE_KEY` - Stripe secret key
- `FRONTEND_URL` - Frontend application URL (for redirects)

---

## Support

For issues or questions:
- Check API status: `GET /health`
- Review error messages in response `detail` field
- Ensure proper authentication tokens are provided
- Verify subscription status if receiving 402 errors

---

## Changelog

### Version 1.0 (Current)
- Initial API release
- User authentication (email/password and Google OAuth)
- Virtual try-on functionality
- Job tracking and status monitoring
- Stripe payment integration
- User profile and usage management

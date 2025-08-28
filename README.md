# Facial Recognition Backend

This is the backend for a facial recognition-based attendance system.

## API Documentation

### Core

#### GET /

Returns a welcome message.

**Response:**

```json
{
  "success": true,
  "message": "Welcome to the Facial Recognition Backend"
}
```

### Attendance

#### POST /api/v1/register

Registers a new student.

**Request:**

This endpoint expects a `multipart/form-data` request with the following fields:

-   `studentId` (string, required): The student's ID.
-   `fullName` (string, required): The student's full name.
-   `password` (string, required): The student's password.
-   `email` (string, optional): The student's email address.
-   `class` (string, optional): The student's class.
-   `profileImage` (file, required): The student's profile image.

**Response (Success):**

```json
{
  "success": true,
  "message": "Student registered successfully.",
  "student": {
    "id": "student123",
    "fullName": "John Doe",
    "email": "john.doe@example.com",
    "class": "Computer Science"
  }
}
```

**Response (Error):**

```json
{
  "success": false,
  "message": "Student with ID 'student123' already exists."
}
```

```json
{
  "success": false,
  "message": "No face found in the image."
}
```

#### POST /api/v1/attendance

Takes attendance by recognizing faces in an uploaded image.

**Request:**

```json
{
  "image": "<base64_encoded_image>"
}
```

**Response (Success):**

```json
{
  "success": true,
  "message": "Attendance recorded.",
  "matchedStudents": [
    {
      "id": "student123",
      "fullName": "John Doe",
      "email": "john.doe@example.com",
      "class": "Computer Science",
      "status": "present",
      "time": "09:30"
    }
  ]
}
```

**Response (Error):**

```json
{
  "success": false,
  "message": "No registered students were recognized."
}
```

```json
{
  "success": false,
  "message": "No faces found in the provided image."
}
```
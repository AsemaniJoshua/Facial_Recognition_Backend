# Facial Recognition Backend

This is the backend for a facial recognition-based attendance system.

## Latest Updates

This update introduces new data models, API endpoints, and refactors existing blueprints to handle an expanded set of features, including dashboard metrics and improved student management.

### Models Update

*   **`Student` Model:**
    *   Now includes `attendance_percent` (Integer), `status` (String), and `last_seen` (DateTime) fields to store more comprehensive student information.
*   **New Models Added:**
    *   **`DashboardMetrics`**: Stores key performance indicators for the dashboard.
        *   Fields: `title` (String), `value` (Integer), `description` (String).
    *   **`Chart`**: Stores data for graphical representation, such as daily attendance.
        *   Fields: `day` (String), `present` (Integer), `absent` (Integer).
    *   **`AttendanceMetrics`**: Stores aggregated attendance statistics.
        *   Fields: `title` (String), `value` (Integer).

### API Endpoints Update

This section details all available API endpoints, grouped by their blueprint. All blueprints under `/api/v1` require authentication.

---

### Core Blueprint

*   **`GET /`**
    
    Returns a welcome message to verify that the API is running.

*   **`POST /api/register`**
    
    Registers a new student with their details and a single profile image.
    
    **Request (`multipart/form-data`):**
    -   `studentId` (string, required): The student's ID.
    -   `fullName` (string, required): The student's full name.
    -   `email` (string, required): The student's email address.
    -   `className` (string, required): The student's class.
    -   `profileImage` (file, required): An image of the student's face.
    
    **Response (Success):**
    ```json
    {
      "success": true,
      "message": "Student registered successfully!",
      "student": {
        "id": "ST005",
        "fullName": "John Doe",
        "email": "john.doe@example.com",
        "class": "Computer Science"
      }
    }
    ```


### Attendance Blueprint (`/api/v1`)

*   **`POST /api/v1/attendance`**
    
    Takes attendance by recognizing faces in a base64 encoded image.
    
    **Request Body:**
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
          "id": "ST001",
          "fullName": "John Doe",
          "status": "present",
          "time": "09:01:15"
        }
      ]
    }
    ```

*   **`GET /api/v1/allattendance`**
    
    Retrieves a list of all attendance records from the database.
    
    **Response (Success):**
    ```json
    {
      "success": true,
      "attendance": [
        {
          "id": "c7a7c8f8-71a6-4c4f-8e09-e8b1e1b1e1b1",
          "student_id": "ST001",
          "date": "2023-10-27",
          "time": "09:01:15",
          "status": "present"
        }
      ]
    }
    ```

*   **`GET /api/v1/attendance/<id>`**
    
    Retrieves a single attendance record by its unique ID.

*   **`GET /api/v1/attendance/student/<student_id>`**
    
    Retrieves all attendance records for a specific student by their ID.

*   **`GET /api/v1/attendance/date/<date>`**
    
    Retrieves all attendance records for a specific date. The date format must be `YYYY-MM-DD`.

*   **`GET /api/v1/attendance/status/<status>`**
    
    Retrieves all attendance records that match a given status (`present`, `absent`, or `late`).

*   **`GET /api/v1/attendance/time/<time>`**
    
    Retrieves all attendance records at a specific time. The time format can be `HH:MM:SS` or `HH:MM`.

---

### Students Blueprint (`/api/v1`)

*   **`GET /api/v1/students`**
    
    Retrieves a list of all registered students.
    
    **Response (Success):**
    ```json
    {
      "success": true,
      "students": [
        {
          "id": "ST001",
          "fullName": "John Doe",
          "email": "john.doe@example.com",
          "class": "Computer Science",
          "status": "active",
          "attendance_percent": 95,
          "last_seen": "2023-10-27T09:01:15",
          "profileImage": "http://example.com/path/to/image.jpg"
        }
      ]
    }
    ```

*   **`GET /api/v1/student/<id>`**
    
    Retrieves a single student by their unique ID.

*   **`GET /api/v1/student/fullname/<fullname>`**
    
    Retrieves a list of students whose full name contains the provided string (case-insensitive).

*   **`GET /api/v1/student/email/<email>`**
    
    Retrieves a single student by their exact email address.

---

### Dashboard Blueprint (`/api/v1`)

*   **`GET /api/v1/dashboard/metrics`**
    
    Retrieves key dashboard metrics, such as total students and daily attendance counts.
    
    **Response (Example):**
    ```json
    [
      {
        "title": "Total Students",
        "value": 320,
        "description": "Total number of registered students"
      },
      {
        "title": "Present Today",
        "value": 18,
        "description": "Students present today"
      }
    ]
    ```

*   **`GET /api/v1/dashboard/chart`**
    
    Retrieves data formatted for a weekly attendance chart.
    
    **Response (Example):**
    ```json
    [
      { "day": "Mon", "present": 29, "absent": 3 },
      { "day": "Tue", "present": 31, "absent": 1 }
    ]
    ```

*   **`GET /api/v1/attendance/metrics`**
    
    Retrieves aggregated attendance metrics (e.g., total present, total late).
    
    **Response (Example):**
    ```json
    [
      { "title": "Present", "value": 2 },
      { "title": "Late", "value": 2 }
    ]
    ```

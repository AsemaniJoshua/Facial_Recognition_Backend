from flask import Blueprint, jsonify

openapi_bp = Blueprint('openapi', __name__, url_prefix='/api/v1/docs')

@openapi_bp.route('/openapi.json', methods=['GET'])
def openapi_spec():
    # Minimal OpenAPI spec, extend as needed
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Facial Recognition Attendance API",
            "version": "1.0.0"
        },
        "paths": {
            "/api/v1/auth/signup": {
                "post": {
                    "summary": "Sign up a new developer account",
                    "responses": {
                        "201": {"description": "Registration successful."},
                        "400": {"description": "Email already exists or missing fields."}
                    }
                }
            },
            "/api/v1/auth/login": {
                "post": {
                    "summary": "Login for developer account",
                    "responses": {
                        "200": {"description": "Login successful."},
                        "401": {"description": "Invalid credentials."}
                    }
                }
            },
            "/api/v1/attendance/mark": {
                "post": {
                    "summary": "Mark attendance for a user",
                    "responses": {
                        "200": {"description": "Attendance marked."},
                        "409": {"description": "Attendance already marked for today."},
                        "401": {"description": "Unauthorized."},
                        "429": {"description": "Rate limit exceeded."}
                    }
                }
            },
            "/api/v1/person/register": {
                "post": {
                    "summary": "Register a person for face recognition",
                    "responses": {
                        "201": {"description": "Person registered."},
                        "400": {"description": "Missing required fields."},
                        "404": {"description": "No faces found."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/person/attendance": {
                "post": {
                    "summary": "Mark attendance for a registered person via face recognition",
                    "responses": {
                        "200": {"description": "Attendance marked."},
                        "404": {"description": "No matching person found or no faces found."},
                        "409": {"description": "Attendance already marked for today."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/bulk/person/register": {
                "post": {
                    "summary": "Bulk register persons for face recognition",
                    "responses": {
                        "200": {"description": "Bulk registration results."},
                        "400": {"description": "Missing or invalid persons list."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/bulk/person/attendance": {
                "post": {
                    "summary": "Bulk mark attendance for persons via face recognition",
                    "responses": {
                        "200": {"description": "Bulk attendance results."},
                        "400": {"description": "Missing or invalid images list."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/admin/face-tolerance": {
                "post": {
                    "summary": "Update face recognition tolerance for account",
                    "responses": {
                        "200": {"description": "Tolerance updated."},
                        "400": {"description": "Invalid tolerance value."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/admin/credentials": {
                "get": {
                    "summary": "Get API credentials for dev account",
                    "responses": {
                        "200": {"description": "Credentials returned."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/admin/credentials/regenerate": {
                "post": {
                    "summary": "Regenerate API credentials",
                    "responses": {
                        "200": {"description": "Credentials regenerated."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/admin/credentials/revoke": {
                "post": {
                    "summary": "Revoke API credentials",
                    "responses": {
                        "200": {"description": "Credentials revoked."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/admin/stats": {
                "get": {
                    "summary": "Get stats for dev account",
                    "responses": {
                        "200": {"description": "Stats returned."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/admin/user": {
                "get": {
                    "summary": "Get user info for dev account",
                    "responses": {
                        "200": {"description": "User info returned."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/auditlog/list": {
                "get": {
                    "summary": "List audit logs for dev account",
                    "responses": {
                        "200": {"description": "Audit logs returned."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/webhook/register": {
                "post": {
                    "summary": "Register a webhook for events",
                    "responses": {
                        "201": {"description": "Webhook registered."},
                        "400": {"description": "Missing url or event."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/webhook/list": {
                "get": {
                    "summary": "List webhooks for dev account",
                    "responses": {
                        "200": {"description": "Webhooks returned."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/webhook/delete/{webhook_id}": {
                "delete": {
                    "summary": "Delete a webhook",
                    "responses": {
                        "200": {"description": "Webhook deleted."},
                        "404": {"description": "Webhook not found."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/webhook/update/{webhook_id}": {
                "put": {
                    "summary": "Update a webhook",
                    "responses": {
                        "200": {"description": "Webhook updated."},
                        "404": {"description": "Webhook not found."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/mfa/setup": {
                "post": {
                    "summary": "Setup MFA email",
                    "responses": {
                        "200": {"description": "MFA email set."},
                        "400": {"description": "Email required."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/mfa/request": {
                "post": {
                    "summary": "Request MFA code (email)",
                    "responses": {
                        "200": {"description": "MFA code sent."},
                        "400": {"description": "MFA email not set."},
                        "401": {"description": "Unauthorized."}
                    }
                }
            },
            "/api/v1/mfa/verify": {
                "post": {
                    "summary": "Verify MFA code",
                    "responses": {
                        "200": {"description": "MFA verified and enabled."},
                        "400": {"description": "Code required or expired."},
                        "401": {"description": "Invalid code or unauthorized."}
                    }
                }
            },
            "/api/v1/health": {
                "get": {
                    "summary": "Health check endpoint",
                    "responses": {
                        "200": {"description": "Service healthy."}
                    }
                }
            }
        }
    }
    return jsonify(spec)

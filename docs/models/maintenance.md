# `Maintenance` Models

This document describes the models related to maintenance requests and comments.

**File:** `backend/app/models/maintenance_model.py`

## `MaintenanceRequest` Model

The `MaintenanceRequest` model represents a maintenance request for a vehicle.

### `MaintenanceStatus` (Enum)

An enumeration that defines the possible statuses of a maintenance request.

*   `PENDING`: The request is pending approval.
*   `APPROVED`: The request has been approved.
*   `REJECTED`: The request has been rejected.
*   `IN_PROGRESS`: The maintenance is in progress.
*   `COMPLETED`: The maintenance has been completed.

### `MaintenanceCategory` (Enum)

An enumeration that defines the possible categories of a maintenance request.

*   `MECHANICAL`: Mechanical issue.
*   `ELECTRICAL`: Electrical issue.
*   `BODYWORK`: Bodywork issue.
*   `OTHER`: Other issue.

### `MaintenanceRequest` (Class)

The main class representing a maintenance request.

**Attributes:**

*   `id` (Integer): The primary key of the request.
*   `problem_description` (Text): A description of the problem.
*   `status` (String): The current status of the request (from `MaintenanceStatus`).
*   `category` (String): The category of the request (from `MaintenanceCategory`).
*   `created_at` (DateTime): The timestamp of when the request was created.
*   `updated_at` (DateTime): The timestamp of when the request was last updated.
*   `manager_notes` (Text): Notes from the manager.
*   `reported_by_id` (Integer): The ID of the user who reported the issue.
*   `approved_by_id` (Integer): The ID of the user who approved the request.
*   `vehicle_id` (Integer): The ID of the vehicle the request is for.
*   `organization_id` (Integer): The ID of the organization the request belongs to.

**Relationships:**

*   `reporter`: Relationship to the `User` model (the user who reported the issue).
*   `approver`: Relationship to the `User` model (the user who approved the request).
*   `vehicle`: Relationship to the `Vehicle` model.
*   `comments`: Relationship to the `MaintenanceComment` model.

## `MaintenanceComment` Model

The `MaintenanceComment` model represents a comment on a maintenance request.

### `MaintenanceComment` (Class)

The main class representing a maintenance comment.

**Attributes:**

*   `id` (Integer): The primary key of the comment.
*   `comment_text` (Text): The text of the comment.
*   `file_url` (String): A URL for a file attached to the comment.
*   `created_at` (DateTime): The timestamp of when the comment was created.
*   `organization_id` (Integer): The ID of the organization the comment belongs to.
*   `request_id` (Integer): The ID of the maintenance request the comment is for.
*   `user_id` (Integer): The ID of the user who wrote the comment.

**Relationships:**

*   `request`: Relationship to the `MaintenanceRequest` model.
*   `user`: Relationship to the `User` model.

# `Notification` Model

The `Notification` model represents a notification in the system.

**File:** `backend/app/models/notification_model.py`

## `Notification` (Class)

The main class representing a notification.

**Attributes:**

*   `id` (Integer): The primary key of the notification.
*   `user_id` (Integer): The ID of the user the notification is for.
*   `message` (Text): The message of the notification.
*   `is_read` (Boolean): A flag to indicate if the notification has been read.
*   `created_at` (DateTime): The timestamp of when the notification was created.
*   `related_vehicle_id` (Integer): The ID of the vehicle related to the notification.
*   `organization_id` (Integer): The ID of the organization the notification belongs to.

**Relationships:**

*   `user`: Relationship to the `User` model.
*   `vehicle`: Relationship to the `Vehicle` model.
*   `organization`: Relationship to the `Organization` model.

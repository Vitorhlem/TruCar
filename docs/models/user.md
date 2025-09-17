# `User` Model

The `User` model represents a user in the system.

**File:** `backend/app/models/user_model.py`

## `UserRole` (Enum)

An enumeration that defines the possible roles of a user.

*   `CLIENTE_ATIVO`: An active client.
*   `CLIENTE_DEMO`: A client with a demo account.
*   `DRIVER`: A driver.

## `User` (Class)

The main class representing a user.

**Attributes:**

*   `id` (Integer): The primary key of the user.
*   `full_name` (String): The full name of the user.
*   `email` (String): The email address of the user.
*   `hashed_password` (String): The hashed password of the user.
*   `employee_id` (String): A unique, automatically generated ID for the user (e.g., `TRC-a1b2c3d4`).
*   `role` (Enum): The role of the user (from `UserRole`).
*   `is_active` (Boolean): A flag to indicate if the user is active.
*   `avatar_url` (String): A URL for the user's avatar.
*   `notify_in_app` (Boolean): A flag to indicate if the user should receive in-app notifications.
*   `notify_by_email` (Boolean): A flag to indicate if the user should receive email notifications.
*   `notification_email` (String): The email address for notifications.
*   `organization_id` (Integer): The ID of the organization the user belongs to.

**Properties:**

*   `is_superuser` (bool): A property that returns `True` if the user is a superuser (based on the `SUPERUSER_EMAILS` setting).

**Relationships:**

*   `organization`: Relationship to the `Organization` model.
*   `freight_orders`: Relationship to the `FreightOrder` model.
*   `journeys`: Relationship to the `Journey` model.
*   `reported_requests`: Relationship to the `MaintenanceRequest` model.
*   `alerts`: Relationship to the `Alert` model.
*   `achievements`: Relationship to the `UserAchievement` model.
*   `documents`: Relationship to the `Document` model.
*   `fuel_logs`: Relationship to the `FuelLog` model.

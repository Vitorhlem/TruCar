# `Alert` Model

The `Alert` model represents an alert in the system.

**File:** `backend/app/models/alert_model.py`

## `AlertLevel` (Enum)

An enumeration that defines the possible levels of an alert.

*   `INFO`: Informational alert.
*   `WARNING`: Warning alert.
*   `CRITICAL`: Critical alert.

## `Alert` (Class)

The main class representing an alert.

**Attributes:**

*   `id` (Integer): The primary key of the alert.
*   `message` (String): The message of the alert.
*   `level` (Enum): The level of the alert (from `AlertLevel`).
*   `timestamp` (DateTime): The timestamp of when the alert was created.
*   `organization_id` (Integer): The ID of the organization the alert belongs to.
*   `vehicle_id` (Integer): The ID of the vehicle the alert is related to.
*   `driver_id` (Integer): The ID of the driver the alert is related to.

**Relationships:**

*   `organization`: Relationship to the `Organization` model.
*   `vehicle`: Relationship to the `Vehicle` model.
*   `driver`: Relationship to the `User` model.

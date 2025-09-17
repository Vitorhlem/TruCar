# `Implement` Model

The `Implement` model represents an implement (e.g., a plow, a seeder) in the system.

**File:** `backend/app/models/implement_model.py`

## `ImplementStatus` (Enum)

An enumeration that defines the possible statuses of an implement.

*   `AVAILABLE`: The implement is available for use.
*   `IN_USE`: The implement is currently in use.
*   `MAINTENANCE`: The implement is under maintenance.

## `Implement` (Class)

The main class representing an implement.

**Attributes:**

*   `id` (Integer): The primary key of the implement.
*   `name` (String): The name of the implement.
*   `brand` (String): The brand of the implement.
*   `model` (String): The model of the implement.
*   `type` (String): The type of the implement (e.g., "Plow", "Seeder").
*   `status` (String): The current status of the implement (from `ImplementStatus`).
*   `year` (Integer): The manufacturing year of the implement.
*   `identifier` (String): A unique identifier for the implement.
*   `organization_id` (Integer): The ID of the organization that owns the implement.

**Relationships:**

*   `organization`: Relationship to the `Organization` model.
*   `journeys`: Relationship to the `Journey` model.

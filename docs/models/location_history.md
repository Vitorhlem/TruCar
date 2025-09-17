# `LocationHistory` Model

The `LocationHistory` model represents a location history entry for a vehicle.

**File:** `backend/app/models/location_history_model.py`

## `LocationHistory` (Class)

The main class representing a location history entry.

**Attributes:**

*   `id` (Integer): The primary key of the location history entry.
*   `latitude` (Float): The latitude of the location.
*   `longitude` (Float): The longitude of the location.
*   `timestamp` (DateTime): The timestamp of the location.
*   `vehicle_id` (Integer): The ID of the vehicle the location history entry is for.
*   `organization_id` (Integer): The ID of the organization the location history entry belongs to.

**Relationships:**

*   `vehicle`: Relationship to the `Vehicle` model.
*   `organization`: Relationship to the `Organization` model.

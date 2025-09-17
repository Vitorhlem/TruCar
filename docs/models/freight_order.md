# `FreightOrder` Model

The `FreightOrder` model represents a freight order in the system.

**File:** `backend/app/models/freight_order_model.py`

## `FreightStatus` (Enum)

An enumeration that defines the possible statuses of a freight order.

*   `OPEN`: The freight order is open and visible to all drivers.
*   `CLAIMED`: The freight order has been claimed by a driver.
*   `PENDING`: The freight order is pending (can be used for "scheduled").
*   `IN_TRANSIT`: The freight order is in transit.
*   `DELIVERED`: The freight order has been delivered.
*   `CANCELED`: The freight order has been canceled.

## `FreightOrder` (Class)

The main class representing a freight order.

**Attributes:**

*   `id` (Integer): The primary key of the freight order.
*   `description` (String): A description of the freight order.
*   `status` (Enum): The current status of the freight order (from `FreightStatus`).
*   `scheduled_start_time` (DateTime): The scheduled start time of the freight order.
*   `scheduled_end_time` (DateTime): The scheduled end time of the freight order.
*   `client_id` (Integer): The ID of the client the freight order is for.
*   `vehicle_id` (Integer): The ID of the vehicle assigned to the freight order.
*   `driver_id` (Integer): The ID of the driver assigned to the freight order.
*   `organization_id` (Integer): The ID of the organization the freight order belongs to.

**Relationships:**

*   `client`: Relationship to the `Client` model.
*   `vehicle`: Relationship to the `Vehicle` model.
*   `driver`: Relationship to the `User` model.
*   `organization`: Relationship to the `Organization` model.
*   `stop_points`: Relationship to the `StopPoint` model.
*   `journeys`: Relationship to the `Journey` model.

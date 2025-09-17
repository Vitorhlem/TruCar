# `StopPoint` Model

The `StopPoint` model represents a stop point in a freight order.

**File:** `backend/app/models/stop_point_model.py`

## `StopPointType` (Enum)

An enumeration that defines the possible types of a stop point.

*   `PICKUP`: A pickup point.
*   `DELIVERY`: A delivery point.

## `StopPointStatus` (Enum)

An enumeration that defines the possible statuses of a stop point.

*   `PENDING`: The stop point is pending.
*   `COMPLETED`: The stop point has been completed.

## `StopPoint` (Class)

The main class representing a stop point.

**Attributes:**

*   `id` (Integer): The primary key of the stop point.
*   `freight_order_id` (Integer): The ID of the freight order the stop point belongs to.
*   `sequence_order` (Integer): The order of the stop point in the sequence.
*   `type` (Enum): The type of the stop point (from `StopPointType`).
*   `status` (Enum): The status of the stop point (from `StopPointStatus`).
*   `address` (String): The address of the stop point.
*   `cargo_description` (String): A description of the cargo at the stop point.
*   `scheduled_time` (DateTime): The scheduled time for the stop point.
*   `actual_arrival_time` (DateTime): The actual arrival time at the stop point.

**Relationships:**

*   `freight_order`: Relationship to the `FreightOrder` model.

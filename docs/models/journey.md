# `Journey` Model

The `Journey` model represents a journey or a trip in the system.

**File:** `backend/app/models/journey_model.py`

## `Journey` (Class)

The main class representing a journey.

**Attributes:**

*   `id` (Integer): The primary key of the journey.
*   `start_time` (DateTime): The start time of the journey.
*   `end_time` (DateTime): The end time of the journey.
*   `start_mileage` (Integer): The starting mileage of the vehicle.
*   `end_mileage` (Integer): The ending mileage of the vehicle.
*   `is_active` (Boolean): A flag to indicate if the journey is active.
*   `trip_type` (String): The type of the trip.
*   `implement_id` (Integer): The ID of the implement used in the journey.
*   `freight_order_id` (Integer): The ID of the freight order associated with the journey.
*   `destination_address` (String): The destination address of the journey.
*   `trip_description` (String): A description of the trip.
*   `start_engine_hours` (Float): The starting engine hours of the vehicle.
*   `end_engine_hours` (Float): The ending engine hours of the vehicle.
*   `vehicle_id` (Integer): The ID of the vehicle used in the journey.
*   `driver_id` (Integer): The ID of the driver who made the journey.
*   `organization_id` (Integer): The ID of the organization the journey belongs to.

**Relationships:**

*   `freight_order`: Relationship to the `FreightOrder` model.
*   `implement`: Relationship to the `Implement` model.
*   `vehicle`: Relationship to the `Vehicle` model.
*   `driver`: Relationship to the `User` model.
*   `organization`: Relationship to the `Organization` model.

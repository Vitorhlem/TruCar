# `Vehicle` Model

The `Vehicle` model represents a vehicle in the system.

**File:** `backend/app/models/vehicle_model.py`

## `VehicleStatus` (Enum)

An enumeration that defines the possible statuses of a vehicle.

*   `AVAILABLE`: The vehicle is available for use.
*   `IN_USE`: The vehicle is currently in use.
*   `MAINTENANCE`: The vehicle is under maintenance.

## `Vehicle` (Class)

The main class representing a vehicle.

**Attributes:**

*   `id` (Integer): The primary key of the vehicle.
*   `brand` (String): The brand of the vehicle.
*   `model` (String): The model of the vehicle.
*   `license_plate` (String): The license plate of the vehicle.
*   `identifier` (String): A unique identifier for the vehicle.
*   `year` (Integer): The manufacturing year of the vehicle.
*   `photo_url` (String): A URL for a photo of the vehicle.
*   `status` (Enum): The current status of the vehicle (from `VehicleStatus`).
*   `current_km` (Integer): The current mileage of the vehicle in kilometers.
*   `current_engine_hours` (Float): The current engine hours of the vehicle.
*   `telemetry_device_id` (String): The ID of the telemetry device installed in the vehicle.
*   `last_latitude` (Float): The last known latitude of the vehicle.
*   `last_longitude` (Float): The last known longitude of the vehicle.
*   `next_maintenance_date` (Date): The date of the next scheduled maintenance.
*   `next_maintenance_km` (Integer): The mileage for the next scheduled maintenance.
*   `maintenance_notes` (Text): Notes related to the vehicle's maintenance.
*   `organization_id` (Integer): The ID of the organization that owns the vehicle.

**Relationships:**

*   `organization`: Relationship to the `Organization` model.
*   `journeys`: Relationship to the `Journey` model.
*   `fuel_logs`: Relationship to the `FuelLog` model.
*   `maintenance_requests`: Relationship to the `MaintenanceRequest` model.
*   `freight_orders`: Relationship to the `FreightOrder` model.
*   `costs`: Relationship to the `VehicleCost` model.
*   `alerts`: Relationship to the `Alert` model.
*   `documents`: Relationship to the `Document` model.

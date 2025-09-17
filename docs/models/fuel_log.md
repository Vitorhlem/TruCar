# `FuelLog` Model

The `FuelLog` model represents a fuel log entry in the system.

**File:** `backend/app/models/fuel_log_model.py`

## `VerificationStatus` (Enum)

An enumeration that defines the possible verification statuses of a fuel log.

*   `VERIFIED`: The fuel log has been verified.
*   `SUSPICIOUS`: The fuel log is suspicious.
*   `UNVERIFIED`: The fuel log has not been verified.
*   `PENDING`: The fuel log is pending verification (for integration logs).

## `FuelLogSource` (Enum)

An enumeration that defines the source of a fuel log.

*   `MANUAL`: The fuel log was entered manually.
*   `INTEGRATION`: The fuel log was created through an integration.

## `FuelLog` (Class)

The main class representing a fuel log.

**Attributes:**

*   `id` (Integer): The primary key of the fuel log.
*   `odometer` (Integer): The odometer reading at the time of refueling.
*   `liters` (Float): The number of liters refueled.
*   `total_cost` (Float): The total cost of the refueling.
*   `vehicle_id` (Integer): The ID of the vehicle that was refueled.
*   `user_id` (Integer): The ID of the user who created the fuel log.
*   `receipt_photo_url` (String): A URL for a photo of the receipt.
*   `timestamp` (DateTime): The timestamp of the fuel log.
*   `verification_status` (Enum): The verification status of the fuel log (from `VerificationStatus`).
*   `provider_transaction_id` (String): The transaction ID from the fuel provider.
*   `provider_name` (String): The name of the fuel provider.
*   `gas_station_name` (String): The name of the gas station.
*   `gas_station_latitude` (Float): The latitude of the gas station.
*   `gas_station_longitude` (Float): The longitude of the gas station.
*   `source` (Enum): The source of the fuel log (from `FuelLogSource`).
*   `organization_id` (Integer): The ID of the organization the fuel log belongs to.

**Relationships:**

*   `organization`: Relationship to the `Organization` model.
*   `vehicle`: Relationship to the `Vehicle` model.
*   `user`: Relationship to the `User` model.

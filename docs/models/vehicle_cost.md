# `VehicleCost` Model

The `VehicleCost` model represents a cost associated with a vehicle.

**File:** `backend/app/models/vehicle_cost_model.py`

## `CostType` (Enum)

An enumeration that defines the possible types of a vehicle cost.

*   `MANUTENCAO`: Maintenance.
*   `COMBUSTIVEL`: Fuel.
*   `PEDAGIO`: Toll.
*   `SEGURO`: Insurance.
*   `PNEU`: Tire.
*   `OUTROS`: Others.

## `VehicleCost` (Class)

The main class representing a vehicle cost.

**Attributes:**

*   `id` (Integer): The primary key of the cost.
*   `description` (String): A description of the cost.
*   `amount` (Float): The amount of the cost.
*   `date` (Date): The date of the cost.
*   `cost_type` (Enum): The type of the cost (from `CostType`).
*   `vehicle_id` (Integer): The ID of the vehicle the cost is associated with.
*   `organization_id` (Integer): The ID of the organization the cost belongs to.

**Relationships:**

*   `vehicle`: Relationship to the `Vehicle` model.

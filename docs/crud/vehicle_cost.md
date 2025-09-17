# `crud_vehicle_cost` Operations

The `crud_vehicle_cost` module contains functions for performing CRUD operations on the `VehicleCost` model.

**File:** `backend/app/crud/crud_vehicle_cost.py`

## Functions

### `create_cost(db: AsyncSession, *, obj_in: VehicleCostCreate, vehicle_id: int, organization_id: int) -> VehicleCost`

*   **Description:** Creates a new cost for a vehicle.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `obj_in` (VehicleCostCreate): The data for the new cost.
    *   `vehicle_id` (int): The ID of the vehicle the cost is associated with.
    *   `organization_id` (int): The ID of the organization the cost belongs to.
*   **Returns:** The newly created `VehicleCost` object.

### `get_costs_by_vehicle(db: AsyncSession, *, vehicle_id: int, skip: int = 0, limit: int = 100) -> List[VehicleCost]`

*   **Description:** Retrieves a list of costs for a specific vehicle, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `vehicle_id` (int): The ID of the vehicle.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `VehicleCost` objects.

# `crud_vehicle` Operations

The `crud_vehicle` module contains functions for performing CRUD operations on the `Vehicle` model.

**File:** `backend/app/crud/crud_vehicle.py`

## Functions

### `get(db: AsyncSession, *, vehicle_id: int, organization_id: int) -> Vehicle | None`

*   **Description:** Retrieves a vehicle by its ID, ensuring it belongs to the specified organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `vehicle_id` (int): The ID of the vehicle to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the vehicle.
*   **Returns:** A `Vehicle` object or `None` if not found.

### `get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 8, search: str | None = None) -> List[Vehicle]`

*   **Description:** Retrieves a list of vehicles for a specific organization, with optional pagination and search.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip (for pagination).
    *   `limit` (int): The maximum number of records to return.
    *   `search` (str | None): An optional search term to filter the results.
*   **Returns:** A list of `Vehicle` objects.

### `count_by_org(db: AsyncSession, *, organization_id: int, search: str | None = None) -> int`

*   **Description:** Counts the total number of vehicles for a specific organization, with optional search.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `search` (str | None): An optional search term to filter the count.
*   **Returns:** The total number of vehicles.

### `update_vehicle_from_telemetry(db: AsyncSession, *, payload: TelemetryPayload) -> Vehicle | None`

*   **Description:** Updates a vehicle's data based on a telemetry payload.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `payload` (TelemetryPayload): The telemetry data payload.
*   **Returns:** The updated `Vehicle` object or `None` if the vehicle is not found.

### `create_with_owner(db: AsyncSession, *, obj_in: VehicleCreate, organization_id: int) -> Vehicle`

*   **Description:** Creates a new vehicle associated with a specific organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `obj_in` (VehicleCreate): The data for the new vehicle.
    *   `organization_id` (int): The ID of the organization that will own the new vehicle.
*   **Returns:** The newly created `Vehicle` object.

### `update(db: AsyncSession, *, db_vehicle: Vehicle, vehicle_in: VehicleUpdate) -> Vehicle`

*   **Description:** Updates an existing vehicle's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_vehicle` (Vehicle): The vehicle object to update.
    *   `vehicle_in` (VehicleUpdate): The new data for the vehicle.
*   **Returns:** The updated `Vehicle` object.

### `remove(db: AsyncSession, *, db_vehicle: Vehicle) -> Vehicle`

*   **Description:** Deletes a vehicle from the database.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_vehicle` (Vehicle): The vehicle object to delete.
*   **Returns:** The deleted `Vehicle` object.

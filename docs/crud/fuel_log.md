# `crud_fuel_log` Operations

The `crud_fuel_log` module contains functions for performing CRUD operations on the `FuelLog` model.

**File:** `backend/app/crud/crud_fuel_log.py`

## Manual Fuel Log Functions

### `create_fuel_log(db: AsyncSession, *, log_in: FuelLogCreate, user_id: int, organization_id: int) -> FuelLog`

*   **Description:** Creates a new manual fuel log entry.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `log_in` (FuelLogCreate): The data for the new fuel log.
    *   `user_id` (int): The ID of the user creating the log.
    *   `organization_id` (int): The ID of the organization the log belongs to.
*   **Returns:** The newly created `FuelLog` object.

### `get_fuel_log(db: AsyncSession, *, log_id: int, organization_id: int) -> Optional[FuelLog]`

*   **Description:** Retrieves a fuel log by its ID, ensuring it belongs to the specified organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `log_id` (int): The ID of the fuel log to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the log.
*   **Returns:** A `FuelLog` object or `None` if not found.

### `get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FuelLog]`

*   **Description:** Retrieves a list of fuel logs for a specific organization, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `FuelLog` objects.

### `get_multi_by_user(db: AsyncSession, *, user_id: int, organization_id: int, skip: int = 0, limit: int = 100) -> List[FuelLog]`

*   **Description:** Retrieves a list of fuel logs for a specific user, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user_id` (int): The ID of the user.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `FuelLog` objects.

### `update_fuel_log(db: AsyncSession, *, db_obj: FuelLog, obj_in: FuelLogUpdate) -> FuelLog`

*   **Description:** Updates an existing fuel log's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (FuelLog): The fuel log object to update.
    *   `obj_in` (FuelLogUpdate): The new data for the fuel log.
*   **Returns:** The updated `FuelLog` object.

### `remove_fuel_log(db: AsyncSession, *, db_obj: FuelLog) -> FuelLog`

*   **Description:** Deletes a fuel log from the database.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (FuelLog): The fuel log object to delete.
*   **Returns:** The deleted `FuelLog` object.

## Fuel Provider Integration Functions

### `_verify_transaction_location(vehicle_coords: Optional[tuple[float, float]], station_coords: tuple[float, float], threshold_km: float = 1.0) -> VerificationStatus`

*   **Description:** Verifies if the vehicle's location is within a certain threshold of the gas station's location.
*   **Parameters:**
    *   `vehicle_coords` (Optional[tuple[float, float]]): The coordinates of the vehicle.
    *   `station_coords` (tuple[float, float]): The coordinates of the gas station.
    *   `threshold_km` (float): The maximum allowed distance in kilometers.
*   **Returns:** A `VerificationStatus` enum value.

### `process_provider_transactions(db: AsyncSession, *, transactions: List[FuelProviderTransaction], organization_id: int)`

*   **Description:** Processes a list of fuel transactions from a provider, creating new fuel logs for them.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `transactions` (List[FuelProviderTransaction]): A list of fuel transactions.
    *   `organization_id` (int): The ID of the organization the transactions belong to.
*   **Returns:** A dictionary with the number of new logs processed.

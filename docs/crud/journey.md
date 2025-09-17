# `crud_journey` Operations

The `crud_journey` module contains functions for performing CRUD operations on the `Journey` model.

**File:** `backend/app/crud/crud_journey.py`

## Functions

### `create_journey(db: AsyncSession, *, journey_in: JourneyCreate, driver_id: int, organization_id: int) -> Journey`

*   **Description:** Creates a new journey.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `journey_in` (JourneyCreate): The data for the new journey.
    *   `driver_id` (int): The ID of the driver for the journey.
    *   `organization_id` (int): The ID of the organization the journey belongs to.
*   **Returns:** The newly created `Journey` object.
*   **Raises:**
    *   `ValueError`: If the vehicle or implement is not found, or if the vehicle ID is missing.
    *   `VehicleNotAvailableError`: If the vehicle or implement is not available.

### `count_journeys_in_current_month(db: AsyncSession, *, organization_id: int) -> int`

*   **Description:** Counts the number of journeys created by an organization in the current month.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** The number of journeys.

### `end_journey(db: AsyncSession, *, db_journey: Journey, journey_in: JourneyUpdate) -> Tuple[Journey, Vehicle]`

*   **Description:** Ends a journey, updating the status of the journey, vehicle, and implement.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_journey` (Journey): The journey to end.
    *   `journey_in` (JourneyUpdate): The data for ending the journey.
*   **Returns:** A tuple containing the updated `Journey` and `Vehicle` objects.

### `get_journey(db: AsyncSession, *, journey_id: int, organization_id: int) -> Optional[Journey]`

*   **Description:** Retrieves a journey by its ID, ensuring it belongs to the specified organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `journey_id` (int): The ID of the journey to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the journey.
*   **Returns:** A `Journey` object or `None` if not found.

### `get_all_journeys(db: AsyncSession, *, organization_id: int, requester_role: UserRole, skip: int = 0, limit: int = 100, driver_id: int | None = None, vehicle_id: int | None = None, date_from: date | None = None, date_to: date | None = None) -> List[Journey]`

*   **Description:** Retrieves a list of all journeys for a specific organization, with various filtering options.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `requester_role` (UserRole): The role of the user requesting the journeys.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
    *   `driver_id` (int | None): An optional driver ID to filter by.
    *   `vehicle_id` (int | None): An optional vehicle ID to filter by.
    *   `date_from` (date | None): An optional start date to filter by.
    *   `date_to` (date | None): An optional end date to filter by.
*   **Returns:** A list of `Journey` objects.

### `get_active_journeys(db: AsyncSession, *, organization_id: int) -> list[Journey]`

*   **Description:** Retrieves a list of all active journeys for a specific organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `Journey` objects.

### `get_active_journey_by_driver(db: AsyncSession, *, driver_id: int, organization_id: int) -> Journey | None`

*   **Description:** Retrieves the active journey for a specific driver.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `driver_id` (int): The ID of the driver.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A `Journey` object or `None` if not found.

### `delete_journey(db: AsyncSession, *, journey_to_delete: Journey) -> Journey`

*   **Description:** Deletes a journey from the database.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `journey_to_delete` (Journey): The journey to delete.
*   **Returns:** The deleted `Journey` object.

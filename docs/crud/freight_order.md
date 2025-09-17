# `crud_freight_order` Operations

The `crud_freight_order` module contains functions for performing CRUD operations on the `FreightOrder` model.

**File:** `backend/app/crud/crud_freight_order.py`

## Functions

### `create_with_stops(db: AsyncSession, *, obj_in: FreightOrderCreate, organization_id: int) -> FreightOrder`

*   **Description:** Creates a new freight order with its associated stop points.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `obj_in` (FreightOrderCreate): The data for the new freight order, including the stop points.
    *   `organization_id` (int): The ID of the organization the freight order will belong to.
*   **Returns:** The newly created `FreightOrder` object.

### `get(db: AsyncSession, *, id: int, organization_id: int) -> FreightOrder | None`

*   **Description:** Retrieves a freight order by its ID, including all its relationships.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `id` (int): The ID of the freight order to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the freight order.
*   **Returns:** A `FreightOrder` object or `None` if not found.

### `get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FreightOrder]`

*   **Description:** Retrieves a list of freight orders for a specific organization, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `FreightOrder` objects.

### `get_multi_by_status(db: AsyncSession, *, organization_id: int, status: FreightStatus) -> List[FreightOrder]`

*   **Description:** Retrieves a list of freight orders for a specific organization with a specific status.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `status` (FreightStatus): The status to filter by.
*   **Returns:** A list of `FreightOrder` objects.

### `get_pending_by_driver(db: AsyncSession, *, driver_id: int, organization_id: int) -> List[FreightOrder]`

*   **Description:** Retrieves the pending (claimed or in-transit) freight orders for a specific driver.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `driver_id` (int): The ID of the driver.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `FreightOrder` objects.

### `update(db: AsyncSession, *, db_obj: FreightOrder, obj_in: FreightOrderUpdate) -> FreightOrder`

*   **Description:** Updates an existing freight order's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (FreightOrder): The freight order object to update.
    *   `obj_in` (FreightOrderUpdate): The new data for the freight order.
*   **Returns:** The updated `FreightOrder` object.

### `claim_order(db: AsyncSession, *, order: FreightOrder, driver: User, vehicle: Vehicle) -> FreightOrder`

*   **Description:** Assigns a freight order to a driver and a vehicle.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `order` (FreightOrder): The freight order to claim.
    *   `driver` (User): The driver to assign the order to.
    *   `vehicle` (Vehicle): The vehicle to assign the order to.
*   **Returns:** The updated `FreightOrder` object.

### `start_journey_for_stop(db: AsyncSession, *, order: FreightOrder, stop: StopPoint, vehicle: Vehicle) -> Journey`

*   **Description:** Starts a new journey for a specific stop point in a freight order.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `order` (FreightOrder): The freight order.
    *   `stop` (StopPoint): The stop point to start the journey for.
    *   `vehicle` (Vehicle): The vehicle used for the journey.
*   **Returns:** The newly created `Journey` object.

### `complete_stop_point(db: AsyncSession, *, order: FreightOrder, stop: StopPoint, journey: Journey, end_mileage: int) -> StopPoint`

*   **Description:** Marks a stop point as completed, finalizes the journey, and updates the vehicle's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `order` (FreightOrder): The freight order.
    *   `stop` (StopPoint): The stop point to complete.
    *   `journey` (Journey): The journey associated with the stop point.
    *   `end_mileage` (int): The final mileage of the vehicle.
*   **Returns:** The updated `StopPoint` object.

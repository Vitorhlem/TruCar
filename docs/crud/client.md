# `crud_client` Operations

The `crud_client` module contains functions for performing CRUD operations on the `Client` model.

**File:** `backend/app/crud/crud_client.py`

## Functions

### `create(db: AsyncSession, *, obj_in: ClientCreate, organization_id: int) -> Client`

*   **Description:** Creates a new client.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `obj_in` (ClientCreate): The data for the new client.
    *   `organization_id` (int): The ID of the organization the client will belong to.
*   **Returns:** The newly created `Client` object.

### `get(db: AsyncSession, *, id: int, organization_id: int) -> Client | None`

*   **Description:** Retrieves a client by its ID, ensuring it belongs to the specified organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `id` (int): The ID of the client to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the client.
*   **Returns:** A `Client` object or `None` if not found.

### `get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[Client]`

*   **Description:** Retrieves a list of clients for a specific organization, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `Client` objects.

### `update(db: AsyncSession, *, db_obj: Client, obj_in: ClientUpdate) -> Client`

*   **Description:** Updates an existing client's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (Client): The client object to update.
    *   `obj_in` (ClientUpdate): The new data for the client.
*   **Returns:** The updated `Client` object.

### `remove(db: AsyncSession, *, db_obj: Client) -> Client`

*   **Description:** Deletes a client from the database.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (Client): The client object to delete.
*   **Returns:** The deleted `Client` object.

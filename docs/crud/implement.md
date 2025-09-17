# `crud_implement` Operations

The `crud_implement` module contains functions for performing CRUD operations on the `Implement` model.

**File:** `backend/app/crud/crud_implement.py`

## Functions

### `create_implement(db: AsyncSession, *, obj_in: ImplementCreate, organization_id: int) -> Implement`

*   **Description:** Creates a new implement associated with an organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `obj_in` (ImplementCreate): The data for the new implement.
    *   `organization_id` (int): The ID of the organization the implement will belong to.
*   **Returns:** The newly created `Implement` object.

### `get_implement(db: AsyncSession, *, implement_id: int, organization_id: int) -> Implement | None`

*   **Description:** Retrieves an implement by its ID, ensuring it belongs to the specified organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `implement_id` (int): The ID of the implement to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the implement.
*   **Returns:** An `Implement` object or `None` if not found.

### `get_all_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[Implement]`

*   **Description:** Retrieves a list of all available implements for a specific organization, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `Implement` objects.

### `get_all_by_org_unfiltered(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[Implement]`

*   **Description:** Retrieves a list of all implements for a specific organization, without filtering by status, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `Implement` objects.

### `update_implement(db: AsyncSession, *, db_obj: Implement, obj_in: ImplementUpdate) -> Implement`

*   **Description:** Updates an existing implement's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (Implement): The implement object to update.
    *   `obj_in` (ImplementUpdate): The new data for the implement.
*   **Returns:** The updated `Implement` object.

### `remove_implement(db: AsyncSession, *, db_obj: Implement) -> Implement`

*   **Description:** Deletes an implement from the database.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (Implement): The implement object to delete.
*   **Returns:** The deleted `Implement` object.

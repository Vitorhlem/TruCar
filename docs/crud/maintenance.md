# `crud_maintenance` Operations

The `crud_maintenance` module contains functions for performing CRUD operations on the `MaintenanceRequest` and `MaintenanceComment` models.

**File:** `backend/app/crud/crud_maintenance.py`

## `MaintenanceRequest` CRUD Functions

### `create_request(db: AsyncSession, *, request_in: MaintenanceRequestCreate, reporter_id: int, organization_id: int) -> MaintenanceRequest`

*   **Description:** Creates a new maintenance request.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `request_in` (MaintenanceRequestCreate): The data for the new maintenance request.
    *   `reporter_id` (int): The ID of the user reporting the issue.
    *   `organization_id` (int): The ID of the organization the request belongs to.
*   **Returns:** The newly created `MaintenanceRequest` object.
*   **Raises:**
    *   `ValueError`: If the vehicle is not found in the organization.

### `get_request(db: AsyncSession, *, request_id: int, organization_id: int) -> MaintenanceRequest | None`

*   **Description:** Retrieves a maintenance request by its ID, ensuring it belongs to the specified organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `request_id` (int): The ID of the request to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the request.
*   **Returns:** A `MaintenanceRequest` object or `None` if not found.

### `get_all_requests(db: AsyncSession, *, organization_id: int, search: str | None = None, skip: int = 0, limit: int = 100) -> List[MaintenanceRequest]`

*   **Description:** Retrieves a list of all maintenance requests for a specific organization, with optional search and pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `search` (str | None): An optional search term to filter the results.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `MaintenanceRequest` objects.

### `update_request_status(db: AsyncSession, *, db_obj: MaintenanceRequest, update_data: MaintenanceRequestUpdate, manager_id: int) -> MaintenanceRequest`

*   **Description:** Updates the status of a maintenance request.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (MaintenanceRequest): The maintenance request object to update.
    *   `update_data` (MaintenanceRequestUpdate): The new status data.
    *   `manager_id` (int): The ID of the manager updating the status.
*   **Returns:** The updated `MaintenanceRequest` object.

## `MaintenanceComment` CRUD Functions

### `create_comment(db: AsyncSession, *, comment_in: MaintenanceCommentCreate, request_id: int, user_id: int, organization_id: int) -> MaintenanceComment`

*   **Description:** Creates a new comment on a maintenance request.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `comment_in` (MaintenanceCommentCreate): The data for the new comment.
    *   `request_id` (int): The ID of the maintenance request.
    *   `user_id` (int): The ID of the user creating the comment.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** The newly created `MaintenanceComment` object.
*   **Raises:**
    *   `ValueError`: If the maintenance request is not found.

### `get_comments_for_request(db: AsyncSession, *, request_id: int, organization_id: int) -> List[MaintenanceComment]`

*   **Description:** Retrieves all comments for a specific maintenance request.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `request_id` (int): The ID of the maintenance request.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `MaintenanceComment` objects.

# `crud_maintenance_comment` Operations

The `crud_maintenance_comment` module contains functions for performing CRUD operations on the `MaintenanceComment` model.

**File:** `backend/app/crud/crud_maintenance_comment.py`

## Functions

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

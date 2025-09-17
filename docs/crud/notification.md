# `crud_notification` Operations

The `crud_notification` module contains functions for performing CRUD operations on the `Notification` model.

**File:** `backend/app/crud/crud_notification.py`

## Functions

### `get_notifications_for_user(db: AsyncSession, *, user_id: int, organization_id: int) -> list[Notification]`

*   **Description:** Retrieves all notifications for a specific user within an organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user_id` (int): The ID of the user.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `Notification` objects.

### `get_unread_notifications_count(db: AsyncSession, *, user_id: int, organization_id: int) -> int`

*   **Description:** Retrieves the count of unread notifications for a specific user within an organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user_id` (int): The ID of the user.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** The number of unread notifications.

### `mark_notification_as_read(db: AsyncSession, *, notification_id: int, user_id: int, organization_id: int) -> Notification | None`

*   **Description:** Marks a notification as read.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `notification_id` (int): The ID of the notification to mark as read.
    *   `user_id` (int): The ID of the user who owns the notification.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** The updated `Notification` object or `None` if not found.

### `create_alert_for_all_managers(db: AsyncSession, *, message: str, organization_id: int, vehicle_id: int | None = None)`

*   **Description:** Creates a notification for all managers of a specific organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `message` (str): The notification message.
    *   `organization_id` (int): The ID of the organization.
    *   `vehicle_id` (int | None): An optional ID of a related vehicle.

### `run_system_checks_for_organization(db: AsyncSession, *, organization_id: int)`

*   **Description:** Runs system checks for a specific organization and generates alerts based on business rules.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization to run the checks for.

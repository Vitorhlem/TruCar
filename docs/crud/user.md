# `crud_user` Operations

The `crud_user` module contains functions for performing CRUD operations on the `User` model.

**File:** `backend/app/crud/crud_user.py`

## Functions

### `get(db: AsyncSession, *, id: int, organization_id: int | None = None) -> User | None`

*   **Description:** Retrieves a user by their ID, with an optional filter for the organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `id` (int): The ID of the user to retrieve.
    *   `organization_id` (int | None): An optional ID of the organization to filter by.
*   **Returns:** A `User` object or `None` if not found.

### `get_user_by_email(db: AsyncSession, *, email: str, load_organization: bool = False) -> User | None`

*   **Description:** Retrieves a user by their email address.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `email` (str): The email address of the user.
    *   `load_organization` (bool): A flag to indicate if the user's organization should be loaded as well.
*   **Returns:** A `User` object or `None` if not found.

### `get_multi_by_org(db: AsyncSession, *, organization_id: int | None = None, skip: int = 0, limit: int = 100) -> List[User]`

*   **Description:** Retrieves a list of users for a specific organization, with optional pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int | None): An optional ID of the organization to filter by.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `User` objects.

### `get_users_by_role(db: AsyncSession, *, role: UserRole, organization_id: int | None = None, skip: int = 0, limit: int = 100) -> List[User]`

*   **Description:** Retrieves a list of users with a specific role, with optional filtering by organization and pagination.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `role` (UserRole): The role to filter by.
    *   `organization_id` (int | None): An optional ID of the organization to filter by.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
*   **Returns:** A list of `User` objects.

### `create(db: AsyncSession, *, user_in: "UserCreate", organization_id: int, role: UserRole) -> User`

*   **Description:** Creates a new user.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user_in` (UserCreate): The data for the new user.
    *   `organization_id` (int): The ID of the organization the user will belong to.
    *   `role` (UserRole): The role of the new user.
*   **Returns:** The newly created `User` object.

### `create_new_organization_and_user(db: AsyncSession, *, user_in: "UserRegister") -> User`

*   **Description:** Creates a new organization and the first user for it.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user_in` (UserRegister): The data for the new user and organization.
*   **Returns:** The newly created `User` object.

### `update(db: AsyncSession, *, db_user: User, user_in: "UserUpdate") -> User`

*   **Description:** Updates an existing user's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_user` (User): The user object to update.
    *   `user_in` (UserUpdate): The new data for the user.
*   **Returns:** The updated `User` object.

### `update_password(db: AsyncSession, *, db_user: User, new_password: str) -> User`

*   **Description:** Updates a user's password.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_user` (User): The user object to update.
    *   `new_password` (str): The new password.
*   **Returns:** The updated `User` object.

### `authenticate(db: AsyncSession, *, email: str, password: str) -> User | None`

*   **Description:** Authenticates a user by email and password.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `email` (str): The user's email address.
    *   `password` (str): The user's password.
*   **Returns:** The authenticated `User` object or `None` if authentication fails.

### `get_leaderboard_data(db: AsyncSession, *, organization_id: int) -> dict`

*   **Description:** Retrieves the leaderboard data for a specific organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A dictionary containing the leaderboard data.

### `get_driver_metrics(db: AsyncSession, *, user: User) -> "DriverMetrics"`

*   **Description:** Retrieves the metrics for a specific driver.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user` (User): The driver to retrieve the metrics for.
*   **Returns:** A `DriverMetrics` object.

### `get_driver_ranking_context(db: AsyncSession, *, user: User) -> List["DriverRankEntry"]`

*   **Description:** Retrieves the ranking context for a specific driver.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user` (User): The driver to retrieve the ranking context for.
*   **Returns:** A list of `DriverRankEntry` objects.

### `get_driver_achievements(db: AsyncSession, *, user: User) -> List["AchievementStatus"]`

*   **Description:** Retrieves the achievements for a specific driver.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user` (User): The driver to retrieve the achievements for.
*   **Returns:** A list of `AchievementStatus` objects.

### `remove(db: AsyncSession, *, db_user: User) -> User`

*   **Description:** Deletes a user from the database.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_user` (User): The user object to delete.
*   **Returns:** The deleted `User` object.

### `activate_user(db: AsyncSession, *, user_to_activate: User) -> User`

*   **Description:** Activates a user by changing their role from `CLIENTE_DEMO` to `CLIENTE_ATIVO`.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user_to_activate` (User): The user to activate.
*   **Returns:** The activated `User` object.

### `count_by_org(db: AsyncSession, *, organization_id: int, role: UserRole | None = None) -> int`

*   **Description:** Counts the number of users in a specific organization, with an optional filter for the role.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `role` (UserRole | None): An optional role to filter by.
*   **Returns:** The number of users.

### `get_user_stats(db: AsyncSession, *, user_id: int, organization_id: int) -> dict | None`

*   **Description:** Calculates the statistics for a specific user, adapted to the organization's sector.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `user_id` (int): The ID of the user.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A dictionary containing the user's statistics or `None` if the user is not found.

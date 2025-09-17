# `crud_organization` Operations

The `crud_organization` module contains functions for performing CRUD operations on the `Organization` model.

**File:** `backend/app/crud/crud_organization.py`

## Functions

### `get(db: AsyncSession, *, id: int) -> Organization | None`

*   **Description:** Retrieves an organization by its ID, loading the associated users.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `id` (int): The ID of the organization to retrieve.
*   **Returns:** An `Organization` object or `None` if not found.

### `get_multi(db: AsyncSession, *, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Organization]`

*   **Description:** Retrieves a list of organizations, with optional pagination and filtering by user status.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
    *   `status` (Optional[str]): An optional status to filter by.
*   **Returns:** A list of `Organization` objects.

### `get_organization_by_name(db: AsyncSession, name: str) -> Organization | None`

*   **Description:** Retrieves an organization by its name.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `name` (str): The name of the organization.
*   **Returns:** An `Organization` object or `None` if not found.

### `create(db: AsyncSession, *, obj_in: OrganizationCreate) -> Organization`

*   **Description:** Creates a new organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `obj_in` (OrganizationCreate): The data for the new organization.
*   **Returns:** The newly created `Organization` object.

### `update(db: AsyncSession, *, db_obj: Organization, obj_in: OrganizationUpdate) -> Organization`

*   **Description:** Updates an existing organization's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (Organization): The organization object to update.
    *   `obj_in` (OrganizationUpdate): The new data for the organization.
*   **Returns:** The updated `Organization` object.

### `update_fuel_integration_settings(db: AsyncSession, *, db_obj: Organization, obj_in: OrganizationFuelIntegrationUpdate) -> Organization`

*   **Description:** Updates the fuel integration settings for an organization, encrypting the credentials before saving.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (Organization): The organization object to update.
    *   `obj_in` (OrganizationFuelIntegrationUpdate): The new fuel integration settings.
*   **Returns:** The updated `Organization` object.

### `get_decrypted_fuel_credentials(organization: Organization) -> dict`

*   **Description:** Decrypts and returns the fuel credentials for an organization. **Warning:** Do not expose this function directly in a public API.
*   **Parameters:**
    *   `organization` (Organization): The organization to retrieve the credentials for.
*   **Returns:** A dictionary containing the decrypted fuel credentials.

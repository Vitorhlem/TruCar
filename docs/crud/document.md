# `crud_document` Operations

The `crud_document` module contains functions for performing CRUD operations on the `Document` model.

**File:** `backend/app/crud/crud_document.py`

## Functions

### `create_with_file_url(db: AsyncSession, *, obj_in: DocumentCreate, organization_id: int, file_url: str) -> Document`

*   **Description:** Creates a new document with a file URL.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `obj_in` (DocumentCreate): The data for the new document.
    *   `organization_id` (int): The ID of the organization the document will belong to.
    *   `file_url` (str): The URL of the document file.
*   **Returns:** The newly created `Document` object.

### `get(db: AsyncSession, *, id: int, organization_id: int) -> Optional[Document]`

*   **Description:** Retrieves a document by its ID, ensuring it belongs to the specified organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `id` (int): The ID of the document to retrieve.
    *   `organization_id` (int): The ID of the organization that owns the document.
*   **Returns:** A `Document` object or `None` if not found.

### `get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100, expiring_in_days: Optional[int] = None) -> List[DocumentPublic]`

*   **Description:** Retrieves a list of documents for a specific organization, with optional pagination and filtering for expiring documents.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `skip` (int): The number of records to skip.
    *   `limit` (int): The maximum number of records to return.
    *   `expiring_in_days` (Optional[int]): An optional number of days to filter for expiring documents.
*   **Returns:** A list of `DocumentPublic` objects.

### `update(db: AsyncSession, *, db_obj: Document, obj_in: DocumentUpdate) -> Document`

*   **Description:** Updates an existing document's data.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `db_obj` (Document): The document object to update.
    *   `obj_in` (DocumentUpdate): The new data for the document.
*   **Returns:** The updated `Document` object.

### `remove(db: AsyncSession, *, id: int, organization_id: int) -> Optional[Document]`

*   **Description:** Deletes a document from the database.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `id` (int): The ID of the document to delete.
    *   `organization_id` (int): The ID of the organization that owns the document.
*   **Returns:** The deleted `Document` object or `None` if not found.

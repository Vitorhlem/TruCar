# `Document` Model

The `Document` model represents a document in the system.

**File:** `backend/app/models/document_model.py`

## `DocumentType` (Enum)

An enumeration that defines the possible types of a document.

*   `CNH`: Driver's License.
*   `CRLV`: Vehicle Registration and Licensing Certificate.
*   `ANTT`: National Land Transport Agency.
*   `ASO`: Occupational Health Certificate.
*   `SEGURO`: Insurance.
*   `OUTRO`: Other.

## `Document` (Class)

The main class representing a document.

**Attributes:**

*   `id` (Integer): The primary key of the document.
*   `document_type` (Enum): The type of the document (from `DocumentType`).
*   `expiry_date` (Date): The expiry date of the document.
*   `file_url` (String): A URL for the document file.
*   `notes` (Text): Notes related to the document.
*   `organization_id` (Integer): The ID of the organization the document belongs to.
*   `vehicle_id` (Integer): The ID of the vehicle the document is associated with.
*   `driver_id` (Integer): The ID of the driver the document is associated with.

**Relationships:**

*   `organization`: Relationship to the `Organization` model.
*   `vehicle`: Relationship to the `Vehicle` model.
*   `driver`: Relationship to the `User` model.

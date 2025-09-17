# `Client` Model

The `Client` model represents a client in the system.

**File:** `backend/app/models/client_model.py`

## `Client` (Class)

The main class representing a client.

**Attributes:**

*   `id` (Integer): The primary key of the client.
*   `name` (String): The name of the client.
*   `contact_person` (String): The contact person for the client.
*   `phone` (String): The phone number of the client.
*   `email` (String): The email address of the client.
*   `organization_id` (Integer): The ID of the organization the client belongs to.

**Relationships:**

*   `organization`: Relationship to the `Organization` model.
*   `freight_orders`: Relationship to the `FreightOrder` model.

# `Organization` Model

The `Organization` model represents an organization in the system.

**File:** `backend/app/models/organization_model.py`

## `Sector` (Enum)

An enumeration that defines the possible sectors of an organization.

*   `AGRONEGOCIO`: Agribusiness.
*   `CONSTRUCAO_CIVIL`: Civil Construction.
*   `SERVICOS`: Services.
*   `FRETE`: Freight.

## `Organization` (Class)

The main class representing an organization.

**Attributes:**

*   `id` (Integer): The primary key of the organization.
*   `name` (String): The name of the organization.
*   `sector` (String): The sector of the organization.
*   `fuel_provider_name` (String): The name of the fuel provider.
*   `encrypted_fuel_provider_api_key` (LargeBinary): The encrypted API key for the fuel provider.
*   `encrypted_fuel_provider_api_secret` (LargeBinary): The encrypted API secret for the fuel provider.

**Relationships:**

*   `users`: Relationship to the `User` model.
*   `vehicles`: Relationship to the `Vehicle` model.
*   `implements`: Relationship to the `Implement` model.
*   `clients`: Relationship to the `Client` model.
*   `freight_orders`: Relationship to the `FreightOrder` model.
*   `alerts`: Relationship to the `Alert` model.
*   `goals`: Relationship to the `Goal` model.
*   `documents`: Relationship to the `Document` model.
*   `fuel_logs`: Relationship to the `FuelLog` model.

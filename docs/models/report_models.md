# Report Models (Pydantic)

This document describes the Pydantic models used for reports and dashboards. These are not database models, but rather data structures used for validation and serialization.

**File:** `backend/app/models/report_models.py`

## `DashboardPodiumDriver`

Represents a driver in the dashboard podium.

**Attributes:**

*   `full_name` (str): The full name of the driver.
*   `avatar_url` (Optional[str]): A URL for the driver's avatar.
*   `primary_metric_value` (float): The value of the primary metric for the driver.

## `CostByCategory`

Represents the total cost for a specific category.

**Attributes:**

*   `cost_type` (str): The type of the cost.
*   `total_amount` (float): The total amount of the cost.

## `DashboardKPIs`

Represents the key performance indicators for the dashboard.

**Attributes:**

*   `total_vehicles` (int): The total number of vehicles.
*   `available_vehicles` (int): The number of available vehicles.
*   `in_use_vehicles` (int): The number of vehicles in use.
*   `maintenance_vehicles` (int): The number of vehicles under maintenance.

## `KmPerDay`

Represents the total kilometers traveled on a specific day.

**Attributes:**

*   `date` (date): The date.
*   `total_km` (float): The total kilometers traveled.

## `UpcomingMaintenance`

Represents an upcoming maintenance for a vehicle.

**Attributes:**

*   `vehicle_info` (str): Information about the vehicle.
*   `due_date` (Optional[date]): The due date for the maintenance.
*   `due_km` (Optional[float]): The due mileage for the maintenance.

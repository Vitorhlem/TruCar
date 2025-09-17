# `crud_report` Operations

The `crud_report` module contains functions for generating reports and dashboard data.

**File:** `backend/app/crud/crud_report.py`

## Helper Functions

### `_format_relative_time(dt: datetime) -> str`

*   **Description:** Formats a datetime object into a relative time string (e.g., '5 minutes ago').
*   **Parameters:**
    *   `dt` (datetime): The datetime object to format.
*   **Returns:** A string representing the relative time.

## Dashboard Functions

### `get_dashboard_kpis(db: AsyncSession, *, organization_id: int) -> dict`

*   **Description:** Retrieves the key performance indicators (KPIs) for the dashboard.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A dictionary containing the dashboard KPIs.

### `get_costs_by_category_last_30_days(db: AsyncSession, *, organization_id: int, start_date: date | None = None) -> List[CostByCategory]`

*   **Description:** Aggregates the total costs by category for the last 30 days.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `start_date` (date | None): An optional start date.
*   **Returns:** A list of `CostByCategory` objects.

### `get_podium_drivers(db: AsyncSession, *, organization_id: int) -> List[DashboardPodiumDriver]`

*   **Description:** Retrieves the top 3 drivers for the dashboard podium.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `DashboardPodiumDriver` objects.

### `get_km_per_day_last_30_days(db: AsyncSession, *, organization_id: int, start_date: date | None = None) -> List[KmPerDay]`

*   **Description:** Calculates the total distance or duration per day for the last 30 days.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `start_date` (date | None): An optional start date.
*   **Returns:** A list of `KmPerDay` objects.

### `get_upcoming_maintenances(db: AsyncSession, *, organization_id: int) -> List[UpcomingMaintenance]`

*   **Description:** Retrieves a list of upcoming maintenances.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `UpcomingMaintenance` objects.

## Advanced Dashboard Functions

### `get_efficiency_kpis(db: AsyncSession, *, organization_id: int, start_date: date) -> KpiEfficiency`

*   **Description:** Calculates efficiency KPIs, such as cost per km and utilization rate.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
    *   `start_date` (date): The start date for the calculation.
*   **Returns:** A `KpiEfficiency` object.

### `get_recent_alerts(db: AsyncSession, *, organization_id: int) -> List[AlertSummary]`

*   **Description:** Retrieves the 5 most recent alerts for the organization.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `AlertSummary` objects.

### `get_active_goal_with_progress(db: AsyncSession, *, organization_id: int) -> Optional[GoalStatus]`

*   **Description:** Retrieves the active goal for the current period and calculates its progress.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A `GoalStatus` object or `None` if no active goal is found.

### `get_vehicle_positions(db: AsyncSession, *, organization_id: int) -> List[VehiclePosition]`

*   **Description:** Retrieves the current position of all vehicles for the map.
*   **Parameters:**
    *   `db` (AsyncSession): The database session.
    *   `organization_id` (int): The ID of the organization.
*   **Returns:** A list of `VehiclePosition` objects.

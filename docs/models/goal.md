# `Goal` Model

The `Goal` model represents a goal in the system.

**File:** `backend/app/models/goal_model.py`

## `Goal` (Class)

The main class representing a goal.

**Attributes:**

*   `id` (Integer): The primary key of the goal.
*   `title` (String): The title of the goal.
*   `target_value` (Float): The target value of the goal.
*   `unit` (String): The unit of the goal (e.g., 'R$', 'km/l', '%').
*   `period_start` (Date): The start date of the goal period.
*   `period_end` (Date): The end date of the goal period.
*   `organization_id` (Integer): The ID of the organization the goal belongs to.

**Relationships:**

*   `organization`: Relationship to the `Organization` model.

# `Achievement` Models

This document describes the models related to achievements.

**File:** `backend/app/models/achievement_model.py`

## `Achievement` Model

The `Achievement` model represents an achievement that can be unlocked by a user.

### `Achievement` (Class)

The main class representing an achievement.

**Attributes:**

*   `id` (Integer): The primary key of the achievement.
*   `code` (String): A unique code for the achievement (e.g., `SAFE_DRIVER_30_DAYS`).
*   `title` (String): The title of the achievement.
*   `description` (String): A description of the achievement.
*   `icon` (String): The icon for the achievement.

## `UserAchievement` Model

The `UserAchievement` model represents the link between a user and an achievement they have unlocked.

### `UserAchievement` (Class)

The main class representing a user's achievement.

**Attributes:**

*   `id` (Integer): The primary key of the user achievement.
*   `user_id` (Integer): The ID of the user who unlocked the achievement.
*   `achievement_id` (Integer): The ID of the achievement that was unlocked.
*   `unlocked_at` (DateTime): The timestamp of when the achievement was unlocked.

**Relationships:**

*   `user`: Relationship to the `User` model.
*   `achievement`: Relationship to the `Achievement` model.

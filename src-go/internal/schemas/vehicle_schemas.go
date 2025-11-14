package schemas

import (
	"time"
)

type VehicleCreate struct {
	Brand              string    `json:"brand" binding:"required"`
	Model              string    `json:"model" binding:"required"`
	Year               int       `json:"year" binding:"required"`
	LicensePlate       *string   `json:"license_plate"`
	Identifier         *string   `json:"identifier"`
	PhotoURL           *string   `json:"photo_url"`
	CurrentKM          int       `json:"current_km"`
	CurrentEngineHours *float64  `json:"current_engine_hours"`
	NextMaintenanceDate *time.Time `json:"next_maintenance_date"`
	NextMaintenanceKM  *int      `json:"next_maintenance_km"`
	MaintenanceNotes   *string   `json:"maintenance_notes"`
	TelemetryDeviceID  *string   `json:"telemetry_device_id"`
}

type VehicleUpdate struct {
	Brand              *string   `json:"brand"`
	Model              *string   `json:"model"`
	Year               *int      `json:"year"`
	LicensePlate       *string   `json:"license_plate"`
	Identifier         *string   `json:"identifier"`
	PhotoURL           *string   `json:"photo_url"`
	Status             *string   `json:"status"`
	CurrentKM          *int      `json:"current_km"`
	CurrentEngineHours *float64  `json:"current_engine_hours"`
	NextMaintenanceDate *time.Time `json:"next_maintenance_date"`
	NextMaintenanceKM  *int      `json:"next_maintenance_km"`
	MaintenanceNotes   *string   `json:"maintenance_notes"`
	TelemetryDeviceID  *string   `json:"telemetry_device_id"`
}

package models

import (
	"time"
)

type VehicleStatus string

const (
	StatusAvailable   VehicleStatus = "Disponível"
	StatusInUse       VehicleStatus = "Em uso"
	StatusMaintenance VehicleStatus = "Em manutenção"
)

type Vehicle struct {
	ID                   uint          `gorm:"primaryKey"`
	Brand                string        `gorm:"size:50;not null"`
	Model                string        `gorm:"size:50;not null"`
	LicensePlate         *string       `gorm:"size:20;unique"`
	Identifier           *string       `gorm:"size:50"`
	Year                 int           `gorm:"not null"`
	PhotoURL             *string       `gorm:"size:512"`
	Status               VehicleStatus `gorm:"type:vehicle_status;not null;default:'Disponível'"`
	CurrentKM            int           `gorm:"not null;default:0"`
	CurrentEngineHours   *float64
	AxleConfiguration    *string `gorm:"size:30"`
	TelemetryDeviceID    *string `gorm:"size:100;uniqueIndex"`
	LastLatitude         *float64
	LastLongitude        *float64
	NextMaintenanceDate  *time.Time
	NextMaintenanceKM    *int
	MaintenanceNotes     *string `gorm:"type:text"`
	OrganizationID       uint    `gorm:"not null"`
	CreatedAt            time.Time
	UpdatedAt            time.Time
}

package models

import "time"

type JourneyType string

const (
	JourneyTypeSpecificDestination JourneyType = "specific_destination"
	JourneyTypeFreeRoam            JourneyType = "free_roam"
)

type Journey struct {
	ID                      uint        `gorm:"primaryKey"`
	StartTime               time.Time   `gorm:"not null"`
	EndTime                 *time.Time
	StartMileage            int         `gorm:"not null"`
	EndMileage              *int
	IsActive                bool        `gorm:"default:true"`
	TripType                JourneyType `gorm:"size:50;not null"`
	ImplementID             *uint
	FreightOrderID          *uint
	TripDescription         *string
	StartEngineHours        *float64
	EndEngineHours          *float64
	DestinationAddress      *string
	DestinationStreet       *string `gorm:"size:255"`
	DestinationNeighborhood *string `gorm:"size:100"`
	DestinationCity         *string `gorm:"size:100"`
	DestinationState        *string `gorm:"size:2"`
	DestinationCEP          *string `gorm:"size:9"`
	VehicleID               uint    `gorm:"not null"`
	DriverID                uint    `gorm:"not null"`
	OrganizationID          uint    `gorm:"not null"`
	CreatedAt               time.Time
	UpdatedAt               time.Time
}

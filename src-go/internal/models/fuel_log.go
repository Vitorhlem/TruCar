package models

import "time"

type VerificationStatus string

const (
	VerificationStatusVerified   VerificationStatus = "Verificado"
	VerificationStatusSuspicious VerificationStatus = "Suspeito"
	VerificationStatusUnverified VerificationStatus = "Não verificado"
	VerificationStatusPending    VerificationStatus = "Pendente"
)

type FuelLogSource string

const (
	FuelLogSourceManual      FuelLogSource = "MANUAL"
	FuelLogSourceIntegration FuelLogSource = "INTEGRATION"
)

type FuelLog struct {
	ID                    uint               `gorm:"primaryKey"`
	Odometer              int                `gorm:"not null"`
	Liters                float64            `gorm:"not null"`
	TotalCost             float64            `gorm:"not null"`
	VehicleID             uint               `gorm:"not null"`
	UserID                uint               `gorm:"not null"`
	ReceiptPhotoURL       *string            `gorm:"size:512"`
	Timestamp             time.Time          `gorm:"not null;default:CURRENT_TIMESTAMP"`
	VerificationStatus    VerificationStatus `gorm:"type:verification_status;not null;default:'Não verificado'"`
	ProviderTransactionID *string            `gorm:"size:255;unique"`
	ProviderName          *string            `gorm:"size:100"`
	GasStationName        *string            `gorm:"size:255"`
	GasStationLatitude    *float64
	GasStationLongitude   *float64
	Source                FuelLogSource      `gorm:"type:fuel_log_source;not null;default:'MANUAL'"`
	OrganizationID        uint               `gorm:"not null"`
	CreatedAt             time.Time
	UpdatedAt             time.Time
}

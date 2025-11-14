package models

import "time"

type ImplementStatus string

const (
	ImplementStatusAvailable ImplementStatus = "Disponível"
	ImplementStatusInUse     ImplementStatus = "Em uso"
)

type Implement struct {
	ID             uint   `gorm:"primaryKey"`
	Name           string `gorm:"size:100;not null"`
	Model          string `gorm:"size:100;not null"`
	OrganizationID uint   `gorm:"not null"`
	Status         ImplementStatus `gorm:"type:implement_status;not null;default:'Disponível'"`
	CreatedAt      time.Time
	UpdatedAt      time.Time
}

package models

import "time"

type MaintenanceStatus string

const (
	MaintenanceStatusPendente    MaintenanceStatus = "PENDENTE"
	MaintenanceStatusAprovada    MaintenanceStatus = "APROVADA"
	MaintenanceStatusRejeitada   MaintenanceStatus = "REJEITADA"
	MaintenanceStatusEmAndamento MaintenanceStatus = "EM ANDAMENTO"
	MaintenanceStatusConcluida   MaintenanceStatus = "CONCLUIDA"
)

type MaintenanceCategory string

const (
	MaintenanceCategoryMechanical MaintenanceCategory = "Mecânica"
	MaintenanceCategoryElectrical MaintenanceCategory = "Elétrica"
	MaintenanceCategoryBodywork   MaintenanceCategory = "Funilaria"
	MaintenanceCategoryOther      MaintenanceCategory = "Outro"
)

type MaintenanceRequest struct {
	ID                 uint                `gorm:"primaryKey"`
	ProblemDescription string              `gorm:"type:text;not null"`
	Status             MaintenanceStatus   `gorm:"type:maintenance_status;not null;default:'PENDENTE'"`
	Category           MaintenanceCategory `gorm:"type:maintenance_category;not null"`
	ManagerNotes       *string             `gorm:"type:text"`
	ReportedByID       *uint
	ApprovedByID       *uint
	VehicleID          uint `gorm:"not null"`
	OrganizationID     uint `gorm:"not null"`
	CreatedAt          time.Time
	UpdatedAt          *time.Time
	Comments           []MaintenanceComment `gorm:"foreignKey:RequestID"`
}

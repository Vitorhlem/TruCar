package models

import "time"

type MaintenanceComment struct {
	ID             uint   `gorm:"primaryKey"`
	CommentText    string `gorm:"type:text;not null"`
	FileURL        *string `gorm:"size:512"`
	OrganizationID uint   `gorm:"not null"`
	RequestID      uint   `gorm:"not null"`
	UserID         *uint
	CreatedAt      time.Time
}

package models

import (
	"time"
)

type UserRole string

const (
	RoleClienteAtivo UserRole = "cliente_ativo"
	RoleClienteDemo  UserRole = "cliente_demo"
	RoleDriver       UserRole = "driver"
)

type User struct {
	ID                          uint      `gorm:"primaryKey"`
	FullName                    string    `gorm:"size:100;index;not null"`
	Email                       string    `gorm:"size:100;uniqueIndex;not null"`
	HashedPassword              string    `gorm:"size:255;not null"`
	EmployeeID                  string    `gorm:"size:50;uniqueIndex;not null"`
	Role                        UserRole  `gorm:"type:user_role;not null"`
	IsActive                    bool      `gorm:"default:true"`
	AvatarURL                   *string   `gorm:"size:512"`
	NotifyInApp                 bool      `gorm:"default:true;not null"`
	NotifyByEmail               bool      `gorm:"default:true;not null"`
	NotificationEmail           *string   `gorm:"size:100"`
	ResetPasswordToken          *string   `gorm:"size:255;index"`
	ResetPasswordTokenExpiresAt *time.Time
	OrganizationID              uint      `gorm:"not null"`
	CreatedAt                   time.Time
	UpdatedAt                   time.Time
}

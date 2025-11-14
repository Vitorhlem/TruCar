package schemas

import "go-api/internal/models"

type UserCreate struct {
	Email      string `json:"email" binding:"required,email"`
	FullName   string `json:"full_name" binding:"required"`
	Password   string `json:"password" binding:"required"`
	Role       models.UserRole `json:"role"`
}

type UserUpdate struct {
	FullName string `json:"full_name"`
	Email    string `json:"email" binding:"email"`
	IsActive *bool  `json:"is_active"`
}

type UserPublic struct {
	ID             uint   `json:"id"`
	Email          string `json:"email"`
	FullName       string `json:"full_name"`
	IsActive       bool   `json:"is_active"`
	OrganizationID uint   `json:"organization_id"`
}

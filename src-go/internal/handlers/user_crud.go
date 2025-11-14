package handlers

import (
	"errors"

	"gorm.io/gorm"

	"go-api/internal/db"
	"go-api/internal/models"
)

func GetUserByID(userID, orgID uint) (*models.User, error) {
	var user models.User
	if err := db.DB.Where("id = ? AND organization_id = ?", userID, orgID).First(&user).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &user, nil
}

func GetUserByEmail(email string) (*models.User, error) {
	var user models.User
	if err := db.DB.Where("email = ?", email).First(&user).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &user, nil
}

func GetUsersByOrganization(orgID uint, skip, limit int) ([]models.User, error) {
	var users []models.User
	if err := db.DB.Where("organization_id = ?", orgID).Offset(skip).Limit(limit).Find(&users).Error; err != nil {
		return nil, err
	}
	return users, nil
}

func CreateUser(user *models.User) error {
	return db.DB.Create(user).Error
}

func UpdateUser(user *models.User) error {
	return db.DB.Save(user).Error
}

func DeleteUser(user *models.User) error {
	return db.DB.Delete(user).Error
}

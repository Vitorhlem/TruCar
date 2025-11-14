package handlers

import (
	"errors"

	"gorm.io/gorm"

	"go-api/internal/db"
	"go-api/internal/models"
)

func CreateFuelLog(fuelLog *models.FuelLog) error {
	return db.DB.Create(fuelLog).Error
}

func GetFuelLogByID(fuelLogID, orgID uint) (*models.FuelLog, error) {
	var fuelLog models.FuelLog
	if err := db.DB.Where("id = ? AND organization_id = ?", fuelLogID, orgID).First(&fuelLog).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &fuelLog, nil
}

func GetFuelLogsByOrganization(orgID uint, skip, limit int) ([]models.FuelLog, error) {
	var fuelLogs []models.FuelLog
	if err := db.DB.Where("organization_id = ?", orgID).Offset(skip).Limit(limit).Find(&fuelLogs).Error; err != nil {
		return nil, err
	}
	return fuelLogs, nil
}

func GetFuelLogsByUser(userID, orgID uint, skip, limit int) ([]models.FuelLog, error) {
	var fuelLogs []models.FuelLog
	if err := db.DB.Where("user_id = ? AND organization_id = ?", userID, orgID).Offset(skip).Limit(limit).Find(&fuelLogs).Error; err != nil {
		return nil, err
	}
	return fuelLogs, nil
}

func UpdateFuelLog(fuelLog *models.FuelLog) error {
	return db.DB.Save(fuelLog).Error
}

func DeleteFuelLog(fuelLog *models.FuelLog) error {
	return db.DB.Delete(fuelLog).Error
}

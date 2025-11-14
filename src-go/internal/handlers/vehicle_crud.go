package handlers

import (
	"errors"

	"gorm.io/gorm"

	"go-api/internal/db"
	"go-api/internal/models"
)

func GetVehicleByID(vehicleID, orgID uint) (*models.Vehicle, error) {
	var vehicle models.Vehicle
	if err := db.DB.Where("id = ? AND organization_id = ?", vehicleID, orgID).First(&vehicle).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &vehicle, nil
}

func GetVehiclesByOrganization(orgID uint, skip, limit int, search string) ([]models.Vehicle, error) {
	var vehicles []models.Vehicle
	query := db.DB.Where("organization_id = ?", orgID)

	if search != "" {
		searchQuery := "%" + search + "%"
		query = query.Where("brand LIKE ? OR model LIKE ? OR license_plate LIKE ? OR identifier LIKE ?", searchQuery, searchQuery, searchQuery, searchQuery)
	}

	if err := query.Offset(skip).Limit(limit).Find(&vehicles).Error; err != nil {
		return nil, err
	}
	return vehicles, nil
}

func CountVehiclesByOrganization(orgID uint, search string) (int64, error) {
	var count int64
	query := db.DB.Model(&models.Vehicle{}).Where("organization_id = ?", orgID)

	if search != "" {
		searchQuery := "%" + search + "%"
		query = query.Where("brand LIKE ? OR model LIKE ? OR license_plate LIKE ? OR identifier LIKE ?", searchQuery, searchQuery, searchQuery, searchQuery)
	}

	if err := query.Count(&count).Error; err != nil {
		return 0, err
	}
	return count, nil
}

func CreateVehicle(vehicle *models.Vehicle) error {
	return db.DB.Create(vehicle).Error
}

func UpdateVehicle(vehicle *models.Vehicle) error {
	return db.DB.Save(vehicle).Error
}

func DeleteVehicle(vehicle *models.Vehicle) error {
	return db.DB.Delete(vehicle).Error
}

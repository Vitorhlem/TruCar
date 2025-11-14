package handlers

import (
	"errors"

	"gorm.io/gorm"

	"go-api/internal/db"
	"go-api/internal/models"
)

func CreateMaintenanceRequest(request *models.MaintenanceRequest) error {
	return db.DB.Create(request).Error
}

func GetMaintenanceRequestByID(requestID, orgID uint) (*models.MaintenanceRequest, error) {
	var request models.MaintenanceRequest
	if err := db.DB.Preload("Comments").Where("id = ? AND organization_id = ?", requestID, orgID).First(&request).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &request, nil
}

func GetMaintenanceRequestsByOrganization(orgID uint, skip, limit int, search string) ([]models.MaintenanceRequest, error) {
	var requests []models.MaintenanceRequest
	query := db.DB.Where("organization_id = ?", orgID)

	if search != "" {
		searchQuery := "%" + search + "%"
		query = query.Joins("JOIN vehicles ON vehicles.id = maintenance_requests.vehicle_id").
			Where("problem_description LIKE ? OR vehicles.brand LIKE ? OR vehicles.model LIKE ?", searchQuery, searchQuery, searchQuery)
	}

	if err := query.Offset(skip).Limit(limit).Find(&requests).Error; err != nil {
		return nil, err
	}
	return requests, nil
}

func UpdateMaintenanceRequestStatus(request *models.MaintenanceRequest) error {
	return db.DB.Save(request).Error
}

func DeleteMaintenanceRequest(request *models.MaintenanceRequest) error {
	return db.DB.Delete(request).Error
}

func CreateMaintenanceComment(comment *models.MaintenanceComment) error {
	return db.DB.Create(comment).Error
}

func GetMaintenanceCommentsByRequestID(requestID, orgID uint) ([]models.MaintenanceComment, error) {
	var comments []models.MaintenanceComment
	if err := db.DB.Where("request_id = ? AND organization_id = ?", requestID, orgID).Find(&comments).Error; err != nil {
		return nil, err
	}
	return comments, nil
}

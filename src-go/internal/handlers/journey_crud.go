package handlers

import (
	"errors"
	"time"

	"gorm.io/gorm"

	"go-api/internal/db"
	"go-api/internal/models"
)

var ErrVehicleNotAvailable = errors.New("vehicle not available")

func CreateJourney(journey *models.Journey) (*models.Journey, error) {
	if journey.ImplementID != nil {
		var implement models.Implement
		if err := db.DB.First(&implement, *journey.ImplementID).Error; err != nil {
			return nil, errors.New("implement not found")
		}
		if implement.Status != models.ImplementStatusAvailable {
			return nil, ErrVehicleNotAvailable
		}
		implement.Status = models.ImplementStatusInUse
		if err := db.DB.Save(&implement).Error; err != nil {
			return nil, err
		}
	}

	var vehicle models.Vehicle
	if err := db.DB.First(&vehicle, journey.VehicleID).Error; err != nil {
		return nil, errors.New("vehicle not found")
	}
	if vehicle.Status != models.StatusAvailable {
		return nil, ErrVehicleNotAvailable
	}
	vehicle.Status = models.StatusInUse

	journey.StartMileage = vehicle.CurrentKM
	journey.StartTime = time.Now()
	journey.IsActive = true

	if err := db.DB.Create(journey).Error; err != nil {
		return nil, err
	}

	if err := db.DB.Save(&vehicle).Error; err != nil {
		return nil, err
	}

	return journey, nil
}

func GetJourneyByID(journeyID, orgID uint) (*models.Journey, error) {
	var journey models.Journey
	if err := db.DB.Where("id = ? AND organization_id = ?", journeyID, orgID).First(&journey).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &journey, nil
}

func GetJourneysByOrganization(orgID uint, skip, limit int, driverID, vehicleID *uint, dateFrom, dateTo *time.Time) ([]models.Journey, error) {
	var journeys []models.Journey
	query := db.DB.Where("organization_id = ?", orgID)

	if driverID != nil {
		query = query.Where("driver_id = ?", *driverID)
	}
	if vehicleID != nil {
		query = query.Where("vehicle_id = ?", *vehicleID)
	}
	if dateFrom != nil {
		query = query.Where("start_time >= ?", *dateFrom)
	}
	if dateTo != nil {
		query = query.Where("start_time < ?", *dateTo)
	}

	if err := query.Offset(skip).Limit(limit).Find(&journeys).Error; err != nil {
		return nil, err
	}
	return journeys, nil
}

func EndJourney(journey *models.Journey, endMileage *int, endEngineHours *float64) (*models.Journey, *models.Vehicle, error) {
	journey.EndTime = new(time.Time)
	*journey.EndTime = time.Now()
	journey.IsActive = false
	journey.EndMileage = endMileage
	journey.EndEngineHours = endEngineHours

	var vehicle models.Vehicle
	if err := db.DB.First(&vehicle, journey.VehicleID).Error; err != nil {
		return nil, nil, errors.New("vehicle not found")
	}
	vehicle.Status = models.StatusAvailable
	if endMileage != nil {
		vehicle.CurrentKM = *endMileage
	}
	if endEngineHours != nil {
		vehicle.CurrentEngineHours = endEngineHours
	}

	if journey.ImplementID != nil {
		var implement models.Implement
		if err := db.DB.First(&implement, *journey.ImplementID).Error; err == nil {
			implement.Status = models.ImplementStatusAvailable
			if err := db.DB.Save(&implement).Error; err != nil {
				return nil, nil, err
			}
		}
	}

	if err := db.DB.Save(journey).Error; err != nil {
		return nil, nil, err
	}
	if err := db.DB.Save(&vehicle).Error; err != nil {
		return nil, nil, err
	}

	return journey, &vehicle, nil
}

func DeleteJourney(journey *models.Journey) error {
	if journey.IsActive {
		var vehicle models.Vehicle
		if err := db.DB.First(&vehicle, journey.VehicleID).Error; err == nil {
			vehicle.Status = models.StatusAvailable
			if err := db.DB.Save(&vehicle).Error; err != nil {
				return err
			}
		}
	}
	return db.DB.Delete(journey).Error
}

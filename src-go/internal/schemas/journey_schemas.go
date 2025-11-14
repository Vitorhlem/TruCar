package schemas

import "go-api/internal/models"

type JourneyCreate struct {
	VehicleID               uint   `json:"vehicle_id" binding:"required"`
	TripType                models.JourneyType `json:"trip_type" binding:"required"`
	DestinationAddress      *string `json:"destination_address"`
	TripDescription         *string `json:"trip_description"`
	ImplementID             *uint   `json:"implement_id"`
	DestinationStreet       *string `json:"destination_street"`
	DestinationNeighborhood *string `json:"destination_neighborhood"`
	DestinationCity         *string `json:"destination_city"`
	DestinationState        *string `json:"destination_state"`
	DestinationCEP          *string `json:"destination_cep"`
}

type JourneyUpdate struct {
	EndMileage     *int     `json:"end_mileage"`
	EndEngineHours *float64 `json:"end_engine_hours"`
}

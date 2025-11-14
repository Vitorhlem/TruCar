package schemas

type FuelLogCreate struct {
	Odometer        int     `json:"odometer" binding:"required"`
	Liters          float64 `json:"liters" binding:"required"`
	TotalCost       float64 `json:"total_cost" binding:"required"`
	VehicleID       uint    `json:"vehicle_id" binding:"required"`
	UserID          *uint   `json:"user_id"`
	ReceiptPhotoURL *string `json:"receipt_photo_url"`
}

type FuelLogUpdate struct {
	Odometer        *int     `json:"odometer"`
	Liters          *float64 `json:"liters"`
	TotalCost       *float64 `json:"total_cost"`
	VehicleID       *uint    `json:"vehicle_id"`
	ReceiptPhotoURL *string  `json:"receipt_photo_url"`
}

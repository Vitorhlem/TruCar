package schemas

import "go-api/internal/models"

type MaintenanceRequestCreate struct {
	ProblemDescription string                       `json:"problem_description" binding:"required"`
	VehicleID          uint                         `json:"vehicle_id" binding:"required"`
	Category           models.MaintenanceCategory `json:"category" binding:"required"`
}

type MaintenanceRequestUpdate struct {
	Status       models.MaintenanceStatus `json:"status" binding:"required"`
	ManagerNotes *string                  `json:"manager_notes"`
}

type MaintenanceCommentCreate struct {
	CommentText string  `json:"comment_text" binding:"required"`
	FileURL     *string `json:"file_url"`
}

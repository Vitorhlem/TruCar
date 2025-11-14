package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	"go-api/internal/models"
	"go-api/internal/schemas"
)

func RegisterVehicleRoutes(router *gin.RouterGroup) {
	router.GET("/vehicles", GetVehicles)
	router.POST("/vehicles", CreateVehicleHandler)
	router.GET("/vehicles/:id", GetVehicle)
	router.PUT("/vehicles/:id", UpdateVehicleHandler)
	router.DELETE("/vehicles/:id", DeleteVehicleHandler)
}

func GetVehicles(c *gin.Context) {
	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	rowsPerPage, _ := strconv.Atoi(c.DefaultQuery("rowsPerPage", "8"))
	search := c.DefaultQuery("search", "")

	skip := (page - 1) * rowsPerPage

	vehicles, err := GetVehiclesByOrganization(orgID, skip, rowsPerPage, search)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch vehicles"})
		return
	}

	totalItems, err := CountVehiclesByOrganization(orgID, search)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count vehicles"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"vehicles": vehicles, "total_items": totalItems})
}

func CreateVehicleHandler(c *gin.Context) {
	var vehicleIn schemas.VehicleCreate
	if err := c.ShouldBindJSON(&vehicleIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	vehicle := models.Vehicle{
		Brand:              vehicleIn.Brand,
		Model:              vehicleIn.Model,
		Year:               vehicleIn.Year,
		LicensePlate:       vehicleIn.LicensePlate,
		Identifier:         vehicleIn.Identifier,
		PhotoURL:           vehicleIn.PhotoURL,
		CurrentKM:          vehicleIn.CurrentKM,
		CurrentEngineHours: vehicleIn.CurrentEngineHours,
		NextMaintenanceDate: vehicleIn.NextMaintenanceDate,
		NextMaintenanceKM:  vehicleIn.NextMaintenanceKM,
		MaintenanceNotes:   vehicleIn.MaintenanceNotes,
		TelemetryDeviceID:  vehicleIn.TelemetryDeviceID,
		OrganizationID:     orgID,
	}

	if err := CreateVehicle(&vehicle); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create vehicle"})
		return
	}

	c.JSON(http.StatusCreated, vehicle)
}

func GetVehicle(c *gin.Context) {
	vehicleID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid vehicle ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	vehicle, err := GetVehicleByID(uint(vehicleID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch vehicle"})
		return
	}

	if vehicle == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Vehicle not found"})
		return
	}

	c.JSON(http.StatusOK, vehicle)
}

func UpdateVehicleHandler(c *gin.Context) {
	vehicleID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid vehicle ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	vehicle, err := GetVehicleByID(uint(vehicleID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch vehicle"})
		return
	}

	if vehicle == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Vehicle not found"})
		return
	}

	var vehicleIn schemas.VehicleUpdate
	if err := c.ShouldBindJSON(&vehicleIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if vehicleIn.Brand != nil {
		vehicle.Brand = *vehicleIn.Brand
	}
	if vehicleIn.Model != nil {
		vehicle.Model = *vehicleIn.Model
	}
	if vehicleIn.Year != nil {
		vehicle.Year = *vehicleIn.Year
	}
	if vehicleIn.LicensePlate != nil {
		vehicle.LicensePlate = vehicleIn.LicensePlate
	}
	if vehicleIn.Identifier != nil {
		vehicle.Identifier = vehicleIn.Identifier
	}
	if vehicleIn.PhotoURL != nil {
		vehicle.PhotoURL = vehicleIn.PhotoURL
	}
	if vehicleIn.Status != nil {
		vehicle.Status = models.VehicleStatus(*vehicleIn.Status)
	}
	if vehicleIn.CurrentKM != nil {
		vehicle.CurrentKM = *vehicleIn.CurrentKM
	}
	if vehicleIn.CurrentEngineHours != nil {
		vehicle.CurrentEngineHours = vehicleIn.CurrentEngineHours
	}
	if vehicleIn.NextMaintenanceDate != nil {
		vehicle.NextMaintenanceDate = vehicleIn.NextMaintenanceDate
	}
	if vehicleIn.NextMaintenanceKM != nil {
		vehicle.NextMaintenanceKM = vehicleIn.NextMaintenanceKM
	}
	if vehicleIn.MaintenanceNotes != nil {
		vehicle.MaintenanceNotes = vehicleIn.MaintenanceNotes
	}
	if vehicleIn.TelemetryDeviceID != nil {
		vehicle.TelemetryDeviceID = vehicleIn.TelemetryDeviceID
	}

	if err := UpdateVehicle(vehicle); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update vehicle"})
		return
	}

	c.JSON(http.StatusOK, vehicle)
}

func DeleteVehicleHandler(c *gin.Context) {
	vehicleID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid vehicle ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	vehicle, err := GetVehicleByID(uint(vehicleID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch vehicle"})
		return
	}

	if vehicle == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Vehicle not found"})
		return
	}

	if err := DeleteVehicle(vehicle); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete vehicle"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Vehicle deleted successfully"})
}

package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	"go-api/internal/models"
	"go-api/internal/schemas"
)

func RegisterFuelLogRoutes(router *gin.RouterGroup) {
	router.GET("/fuel-logs", GetFuelLogs)
	router.POST("/fuel-logs", CreateFuelLogHandler)
	router.GET("/fuel-logs/:id", GetFuelLog)
	router.PUT("/fuel-logs/:id", UpdateFuelLogHandler)
	router.DELETE("/fuel-logs/:id", DeleteFuelLogHandler)
}

func GetFuelLogs(c *gin.Context) {
	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	userID := user.ID
	orgID := user.OrganizationID
	userRole := user.Role

	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	var fuelLogs []models.FuelLog

	if userRole == models.RoleClienteAtivo || userRole == models.RoleClienteDemo {
		fuelLogs, err = GetFuelLogsByOrganization(orgID, skip, limit)
	} else {
		fuelLogs, err = GetFuelLogsByUser(userID, orgID, skip, limit)
	}

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch fuel logs"})
		return
	}

	c.JSON(http.StatusOK, fuelLogs)
}

func CreateFuelLogHandler(c *gin.Context) {
	var fuelLogIn schemas.FuelLogCreate
	if err := c.ShouldBindJSON(&fuelLogIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	currentUser, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	currentUserID := currentUser.ID
	orgID := currentUser.OrganizationID

	userID := currentUserID
	if fuelLogIn.UserID != nil {
		userID = *fuelLogIn.UserID
	}

	fuelLog := models.FuelLog{
		Odometer:        fuelLogIn.Odometer,
		Liters:          fuelLogIn.Liters,
		TotalCost:       fuelLogIn.TotalCost,
		VehicleID:       fuelLogIn.VehicleID,
		UserID:          userID,
		ReceiptPhotoURL: fuelLogIn.ReceiptPhotoURL,
		OrganizationID:  orgID,
	}

	if err := CreateFuelLog(&fuelLog); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create fuel log"})
		return
	}

	c.JSON(http.StatusCreated, fuelLog)
}

func GetFuelLog(c *gin.Context) {
	fuelLogID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid fuel log ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	fuelLog, err := GetFuelLogByID(uint(fuelLogID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch fuel log"})
		return
	}
	if fuelLog == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Fuel log not found"})
		return
	}

	c.JSON(http.StatusOK, fuelLog)
}

func UpdateFuelLogHandler(c *gin.Context) {
	fuelLogID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid fuel log ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	fuelLog, err := GetFuelLogByID(uint(fuelLogID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch fuel log"})
		return
	}
	if fuelLog == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Fuel log not found"})
		return
	}

	var fuelLogIn schemas.FuelLogUpdate
	if err := c.ShouldBindJSON(&fuelLogIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if fuelLogIn.Odometer != nil {
		fuelLog.Odometer = *fuelLogIn.Odometer
	}
	if fuelLogIn.Liters != nil {
		fuelLog.Liters = *fuelLogIn.Liters
	}
	if fuelLogIn.TotalCost != nil {
		fuelLog.TotalCost = *fuelLogIn.TotalCost
	}
	if fuelLogIn.VehicleID != nil {
		fuelLog.VehicleID = *fuelLogIn.VehicleID
	}
	if fuelLogIn.ReceiptPhotoURL != nil {
		fuelLog.ReceiptPhotoURL = fuelLogIn.ReceiptPhotoURL
	}

	if err := UpdateFuelLog(fuelLog); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update fuel log"})
		return
	}

	c.JSON(http.StatusOK, fuelLog)
}

func DeleteFuelLogHandler(c *gin.Context) {
	fuelLogID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid fuel log ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	fuelLog, err := GetFuelLogByID(uint(fuelLogID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch fuel log"})
		return
	}
	if fuelLog == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Fuel log not found"})
		return
	}

	if err := DeleteFuelLog(fuelLog); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete fuel log"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

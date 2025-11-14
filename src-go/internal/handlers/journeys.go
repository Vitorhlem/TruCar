package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"

	"go-api/internal/models"
	"go-api/internal/schemas"
)

func RegisterJourneyRoutes(router *gin.RouterGroup) {
	router.GET("/journeys", GetJourneys)
	router.POST("/journeys/start", StartJourneyHandler)
	router.PUT("/journeys/:id/end", EndJourneyHandler)
	router.DELETE("/journeys/:id", DeleteJourneyHandler)
}

func GetJourneys(c *gin.Context) {
	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	var driverID, vehicleID *uint
	if val, err := strconv.Atoi(c.Query("driver_id")); err == nil {
		id := uint(val)
		driverID = &id
	}
	if val, err := strconv.Atoi(c.Query("vehicle_id")); err == nil {
		id := uint(val)
		vehicleID = &id
	}

	var dateFrom, dateTo *time.Time
	if val, err := time.Parse("2006-01-02", c.Query("date_from")); err == nil {
		dateFrom = &val
	}
	if val, err := time.Parse("2006-01-02", c.Query("date_to")); err == nil {
		dateTo = &val
	}

	journeys, err := GetJourneysByOrganization(orgID, skip, limit, driverID, vehicleID, dateFrom, dateTo)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch journeys"})
		return
	}

	c.JSON(http.StatusOK, journeys)
}

func StartJourneyHandler(c *gin.Context) {
	var journeyIn schemas.JourneyCreate
	if err := c.ShouldBindJSON(&journeyIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	driverID := user.ID
	orgID := user.OrganizationID

	journey := models.Journey{
		VehicleID:               journeyIn.VehicleID,
		TripType:                journeyIn.TripType,
		DestinationAddress:      journeyIn.DestinationAddress,
		TripDescription:         journeyIn.TripDescription,
		ImplementID:             journeyIn.ImplementID,
		DestinationStreet:       journeyIn.DestinationStreet,
		DestinationNeighborhood: journeyIn.DestinationNeighborhood,
		DestinationCity:         journeyIn.DestinationCity,
		DestinationState:        journeyIn.DestinationState,
		DestinationCEP:          journeyIn.DestinationCEP,
		DriverID:                driverID,
		OrganizationID:          orgID,
	}

	createdJourney, err := CreateJourney(&journey)
	if err != nil {
		if err == ErrVehicleNotAvailable {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to start journey"})
		return
	}

	c.JSON(http.StatusCreated, createdJourney)
}

func EndJourneyHandler(c *gin.Context) {
	journeyID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid journey ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	journey, err := GetJourneyByID(uint(journeyID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch journey"})
		return
	}
	if journey == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Journey not found"})
		return
	}

	var journeyIn schemas.JourneyUpdate
	if err := c.ShouldBindJSON(&journeyIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	endedJourney, updatedVehicle, err := EndJourney(journey, journeyIn.EndMileage, journeyIn.EndEngineHours)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to end journey"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"journey": endedJourney, "vehicle": updatedVehicle})
}

func DeleteJourneyHandler(c *gin.Context) {
	journeyID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid journey ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	journey, err := GetJourneyByID(uint(journeyID), orgID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch journey"})
		return
	}
	if journey == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Journey not found"})
		return
	}

	if err := DeleteJourney(journey); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete journey"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

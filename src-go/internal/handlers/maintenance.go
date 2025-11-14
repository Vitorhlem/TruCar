package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	"go-api/internal/models"
	"go-api/internal/schemas"
)

func RegisterMaintenanceRoutes(router *gin.RouterGroup) {
	router.GET("/maintenance", GetMaintenanceRequests)
	router.POST("/maintenance", CreateMaintenanceRequestHandler)
	router.GET("/maintenance/:id", GetMaintenanceRequest)
	router.PUT("/maintenance/:id/status", UpdateMaintenanceRequestStatusHandler)
	router.DELETE("/maintenance/:id", DeleteMaintenanceRequestHandler)
	router.GET("/maintenance/:id/comments", GetMaintenanceCommentsHandler)
	router.POST("/maintenance/:id/comments", CreateMaintenanceCommentHandler)
}

func GetMaintenanceRequests(c *gin.Context) {
	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	orgID := user.OrganizationID

	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))
	search := c.DefaultQuery("search", "")

	requests, err := GetMaintenanceRequestsByOrganization(orgID, skip, limit, search)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch maintenance requests"})
		return
	}

	c.JSON(http.StatusOK, requests)
}

func CreateMaintenanceRequestHandler(c *gin.Context) {
	var reqIn schemas.MaintenanceRequestCreate
	if err := c.ShouldBindJSON(&reqIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	req := models.MaintenanceRequest{
		ProblemDescription: reqIn.ProblemDescription,
		VehicleID:          reqIn.VehicleID,
		Category:           reqIn.Category,
		ReportedByID:       &user.ID,
		OrganizationID:     user.OrganizationID,
	}

	if err := CreateMaintenanceRequest(&req); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create maintenance request"})
		return
	}

	c.JSON(http.StatusCreated, req)
}

func GetMaintenanceRequest(c *gin.Context) {
	reqID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	req, err := GetMaintenanceRequestByID(uint(reqID), user.OrganizationID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch maintenance request"})
		return
	}
	if req == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Maintenance request not found"})
		return
	}

	c.JSON(http.StatusOK, req)
}

func UpdateMaintenanceRequestStatusHandler(c *gin.Context) {
	reqID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request ID"})
		return
	}

	var reqIn schemas.MaintenanceRequestUpdate
	if err := c.ShouldBindJSON(&reqIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	req, err := GetMaintenanceRequestByID(uint(reqID), user.OrganizationID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch maintenance request"})
		return
	}
	if req == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Maintenance request not found"})
		return
	}

	req.Status = reqIn.Status
	req.ManagerNotes = reqIn.ManagerNotes
	req.ApprovedByID = &user.ID

	if err := UpdateMaintenanceRequestStatus(req); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update maintenance request"})
		return
	}

	c.JSON(http.StatusOK, req)
}

func DeleteMaintenanceRequestHandler(c *gin.Context) {
	reqID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	req, err := GetMaintenanceRequestByID(uint(reqID), user.OrganizationID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch maintenance request"})
		return
	}
	if req == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Maintenance request not found"})
		return
	}

	if err := DeleteMaintenanceRequest(req); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete maintenance request"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

func GetMaintenanceCommentsHandler(c *gin.Context) {
	reqID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request ID"})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	comments, err := GetMaintenanceCommentsByRequestID(uint(reqID), user.OrganizationID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch comments"})
		return
	}

	c.JSON(http.StatusOK, comments)
}

func CreateMaintenanceCommentHandler(c *gin.Context) {
	reqID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request ID"})
		return
	}

	var commentIn schemas.MaintenanceCommentCreate
	if err := c.ShouldBindJSON(&commentIn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := GetAuthenticatedUser(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	comment := models.MaintenanceComment{
		CommentText:    commentIn.CommentText,
		FileURL:        commentIn.FileURL,
		RequestID:      uint(reqID),
		UserID:         &user.ID,
		OrganizationID: user.OrganizationID,
	}

	if err := CreateMaintenanceComment(&comment); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create comment"})
		return
	}

	c.JSON(http.StatusCreated, comment)
}

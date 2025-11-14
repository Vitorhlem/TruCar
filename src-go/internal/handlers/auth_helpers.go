package handlers

import (
	"errors"

	"github.com/gin-gonic/gin"

	"go-api/internal/models"
)

func GetAuthenticatedUser(c *gin.Context) (*models.User, error) {
	userID, exists := c.Get("userID")
	if !exists {
		return nil, errors.New("user not authenticated")
	}

	user, err := GetUserByID(userID.(uint), 0) // We don't check org here
	if err != nil || user == nil {
		return nil, errors.New("invalid user")
	}
	return user, nil
}

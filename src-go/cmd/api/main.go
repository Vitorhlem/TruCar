package main

import (
	"log"

	"github.com/gin-gonic/gin"

	"go-api/internal/db"
	"go-api/internal/handlers"
	"go-api/internal/middleware"
)

func main() {
	db.InitDB()

	router := gin.Default()

	api := router.Group("/api/v1")
	{
		handlers.RegisterLoginRoutes(api)

		authRequired := api.Group("/")
		authRequired.Use(middleware.AuthMiddleware())
		{
			handlers.RegisterUserRoutes(authRequired)
			handlers.RegisterVehicleRoutes(authRequired)
			handlers.RegisterJourneyRoutes(authRequired)
			handlers.RegisterFuelLogRoutes(authRequired)
			handlers.RegisterMaintenanceRoutes(authRequired)
		}
	}

	if err := router.Run(":8080"); err != nil {
		log.Fatal("Failed to run server:", err)
	}
}

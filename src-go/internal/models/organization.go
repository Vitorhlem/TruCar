package models

import "time"

type Sector string

const (
	TransporteDeCargas      Sector = "Transporte de Cargas"
	TransporteDePassageiros Sector = "Transporte de Passageiros"
	Agronegocio             Sector = "Agronegócio"
	Construcao              Sector = "Construção"
	ServicosDeEntrega       Sector = "Serviços de Entrega"
	Outros                  Sector = "Outros"
)

type Organization struct {
	ID           uint   `gorm:"primaryKey"`
	Name         string `gorm:"size:100;index;not null"`
	Sector       Sector `gorm:"type:sector;not null"`
	VehicleLimit int    `gorm:"default:5;not null"`
	DriverLimit  int    `gorm:"default:10;not null"`
	Users        []User
	CreatedAt    time.Time
	UpdatedAt    time.Time
}

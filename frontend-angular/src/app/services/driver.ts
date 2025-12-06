import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface Journey {
  id: string;
  origin: string;
  destination: string;
  startTime: Date;
  endTime?: Date;
  status: 'active' | 'completed';
  distance: number;
  vehicle: string;
}

export interface FuelLog {
  id: string;
  date: Date;
  vehicle: string;
  liters: number;
  cost: number;
  station: string;
}

export interface Fine {
  id: string;
  date: Date;
  vehicle: string;
  amount: number;
  reason: string;
  status: 'paid' | 'pending';
  location: string;
}

export interface Maintenance {
  id: string;
  date: Date;
  vehicle: string;
  type: string;
  cost: number;
  status: 'scheduled' | 'completed';
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class DriverService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getJourneys(): Observable<Journey[]> {
    return this.http.get<Journey[]>(`${this.apiUrl}/journeys/`);
  }

  getFuelLogs(): Observable<FuelLog[]> {
    return this.http.get<FuelLog[]>(`${this.apiUrl}/fuel-logs/`);
  }

  getFines(): Observable<Fine[]> {
    return this.http.get<Fine[]>(`${this.apiUrl}/fines/`);
  }

  getMaintenanceRecords(): Observable<Maintenance[]> {
    return this.http.get<Maintenance[]>(`${this.apiUrl}/maintenance/`);
  }

  // Active Journey Management (Mock implementation for now to support Cockpit)
  // In a real app, this would fetch from backend
  private activeJourney = signal<Journey | null>(null);

  getActiveJourney() {
    return this.activeJourney;
  }

  startJourney(vehicleId: string) {
    // Simulate backend call
    const newJourney: Journey = {
      id: 'j-' + Date.now(),
      vehicle: vehicleId,
      startTime: new Date(),
      status: 'active',
      origin: 'Current Location',
      destination: 'TBD',
      distance: 0
    };
    this.activeJourney.set(newJourney);
    // this.http.post(`${this.apiUrl}/journeys/start`, { vehicleId }).subscribe();
  }

  stopJourney() {
    this.activeJourney.update((j: Journey | null) => j ? { ...j, status: 'completed', endTime: new Date() } : null);
    setTimeout(() => this.activeJourney.set(null), 2000);
    // this.http.post(`${this.apiUrl}/journeys/stop`, {}).subscribe();
  }
}

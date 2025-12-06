import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface Vehicle {
  id: string;
  brand: string;
  model: string;
  plate: string;
  year: number;
  status: 'active' | 'maintenance' | 'inactive';
  mileage: number;
  fuel_level: number;
  image?: string;
}

@Injectable({
  providedIn: 'root'
})
export class VehicleService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/vehicles`;

  getVehicles(): Observable<Vehicle[]> {
    return this.http.get<Vehicle[]>(`${this.apiUrl}/`);
  }

  getVehicleById(id: string): Observable<Vehicle> {
    return this.http.get<Vehicle>(`${this.apiUrl}/${id}`);
  }
}

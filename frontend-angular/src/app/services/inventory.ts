import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface Part {
  id: string;
  code: string;
  name: string;
  category: string;
  quantity: number;
  minQuantity: number;
  price: number;
  location: string;
}

export interface InventoryItem {
  id: string;
  sku: string;
  name: string;
  status: 'in-stock' | 'low-stock' | 'out-of-stock';
  quantity: number;
  location: string;
}

export interface Implement {
  id: string;
  type: string;
  name: string;
  status: 'available' | 'in-use' | 'maintenance';
  vehicle?: string;
}

@Injectable({
  providedIn: 'root'
})
export class InventoryService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getParts(): Observable<Part[]> {
    return this.http.get<Part[]>(`${this.apiUrl}/parts/`);
  }

  getInventoryItems(): Observable<InventoryItem[]> {
    // Assuming a generic inventory endpoint or mapping to parts/components
    return this.http.get<InventoryItem[]>(`${this.apiUrl}/parts/`);
  }

  getItemById(id: string): Observable<InventoryItem> {
    return this.http.get<InventoryItem>(`${this.apiUrl}/parts/${id}`);
  }

  getImplements(): Observable<Implement[]> {
    return this.http.get<Implement[]>(`${this.apiUrl}/implements/`);
  }
}

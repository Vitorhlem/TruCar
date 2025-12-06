import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface FreightOrder {
  id: string;
  status: 'pending' | 'in-transit' | 'delivered';
  client: string;
  origin: string;
  destination: string;
  date: Date;
  value: number;
}

export interface Client {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  email: string;
  phone: string;
  address: string;
}

export interface Document {
  id: string;
  type: string;
  name: string;
  date: Date;
  status: 'valid' | 'expired' | 'pending';
  url: string;
}

@Injectable({
  providedIn: 'root'
})
export class OperationsService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getFreightOrders(): Observable<FreightOrder[]> {
    return this.http.get<FreightOrder[]>(`${this.apiUrl}/freight-orders/`);
  }

  getClients(): Observable<Client[]> {
    return this.http.get<Client[]>(`${this.apiUrl}/clients/`);
  }

  getDocuments(): Observable<Document[]> {
    return this.http.get<Document[]>(`${this.apiUrl}/documents/`);
  }
}

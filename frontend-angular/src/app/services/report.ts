import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface AuditLog {
  id: string;
  user: string;
  action: string;
  details: string;
  date: Date;
  ip: string;
}

export interface Cost {
  id: string;
  category: string;
  amount: number;
  date: Date;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getAuditLogs(): Observable<AuditLog[]> {
    return this.http.get<AuditLog[]>(`${this.apiUrl}/audit-logs/`);
  }

  getCosts(): Observable<Cost[]> {
    return this.http.get<Cost[]>(`${this.apiUrl}/costs/`);
  }
}

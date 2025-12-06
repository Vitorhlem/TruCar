import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-fuel-logs',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fuel-logs.html',
  styleUrl: './fuel-logs.scss'
})
export class FuelLogsComponent {
  logs = signal([
    { id: '1', date: new Date(), vehicle: 'ABC-1234', liters: 45, cost: 250.00, station: 'Posto Shell' },
    { id: '2', date: new Date(Date.now() - 86400000), vehicle: 'ABC-1234', liters: 50, cost: 280.00, station: 'Posto Ipiranga' },
  ]);
}

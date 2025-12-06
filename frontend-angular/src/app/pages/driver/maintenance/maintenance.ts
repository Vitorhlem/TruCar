import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-maintenance',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './maintenance.html',
  styleUrl: './maintenance.scss'
})
export class MaintenanceComponent {
  maintenances = signal([
    { id: '1', vehicle: 'ABC-1234', type: 'Preventive', description: 'Oil Change', date: new Date(), status: 'scheduled', cost: 350.00 },
    { id: '2', vehicle: 'XYZ-9876', type: 'Corrective', description: 'Brake Pads Replacement', date: new Date(Date.now() - 604800000), status: 'completed', cost: 850.00 },
  ]);
}

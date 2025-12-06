import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { VehicleService } from '../../../services/vehicle';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-vehicles',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vehicles.html',
  styleUrl: './vehicles.scss'
})
export class VehiclesComponent {
  private vehicleService = inject(VehicleService);
  vehicles = toSignal(this.vehicleService.getVehicles(), { initialValue: [] });
}


import { Component, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VehicleService } from '../../../services/vehicle';
import { toSignal } from '@angular/core/rxjs-interop';
import { switchMap } from 'rxjs/operators';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-vehicle-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './vehicle-details.html',
  styleUrl: './vehicle-details.scss'
})
export class VehicleDetailsComponent {
  private route = inject(ActivatedRoute);
  private vehicleService = inject(VehicleService);

  // Using toSignal with route params to fetch data
  vehicle = toSignal(
    this.route.paramMap.pipe(
      switchMap(params => this.vehicleService.getVehicleById(params.get('id')!))
    )
  );
}

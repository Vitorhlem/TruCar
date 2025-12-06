import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DriverService } from '../../../services/driver';

import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-journeys',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './journeys.html',
  styleUrl: './journeys.scss'
})
export class JourneysComponent {
  private driverService = inject(DriverService);
  journeys = toSignal(this.driverService.getJourneys(), { initialValue: [] });
}

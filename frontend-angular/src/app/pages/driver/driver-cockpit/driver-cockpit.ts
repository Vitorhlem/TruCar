import { Component, inject, Signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DriverService, Journey } from '../../../services/driver';


@Component({
  selector: 'app-driver-cockpit',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './driver-cockpit.html',
  styleUrl: './driver-cockpit.scss'
})
export class DriverCockpitComponent {
  private driverService = inject(DriverService);
  activeJourney = this.driverService.getActiveJourney();

  startJourney() {
    this.driverService.startJourney('ABC-1234'); // Hardcoded vehicle for demo
  }

  stopJourney() {
    this.driverService.stopJourney();
  }
}

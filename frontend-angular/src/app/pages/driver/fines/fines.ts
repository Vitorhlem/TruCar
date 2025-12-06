import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DriverService } from '../../../services/driver';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-fines',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fines.html',
  styleUrl: './fines.scss'
})
export class FinesComponent {
  private driverService = inject(DriverService);
  fines = toSignal(this.driverService.getFines(), { initialValue: [] });
}


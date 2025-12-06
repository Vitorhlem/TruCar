import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReportService } from '../../../services/report';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-costs',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './costs.html',
  styleUrl: './costs.scss'
})
export class CostsComponent {
  private reportService = inject(ReportService);
  costs = toSignal(this.reportService.getCosts(), { initialValue: [] });
}

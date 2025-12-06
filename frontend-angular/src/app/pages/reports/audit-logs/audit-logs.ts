import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReportService } from '../../../services/report';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-audit-logs',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './audit-logs.html',
  styleUrl: './audit-logs.scss'
})
export class AuditLogsComponent {
  private reportService = inject(ReportService);
  logs = toSignal(this.reportService.getAuditLogs(), { initialValue: [] });
}

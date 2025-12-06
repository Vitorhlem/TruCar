import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OperationsService } from '../../../services/operations';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-clients',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './clients.html',
  styleUrl: './clients.scss'
})
export class ClientsComponent {
  private operationsService = inject(OperationsService);
  clients = toSignal(this.operationsService.getClients(), { initialValue: [] });
}

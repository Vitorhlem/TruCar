import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OperationsService } from '../../../services/operations';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-freight-orders',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './freight-orders.html',
  styleUrl: './freight-orders.scss'
})
export class FreightOrdersComponent {
  private operationsService = inject(OperationsService);
  orders = toSignal(this.operationsService.getFreightOrders(), { initialValue: [] });
}

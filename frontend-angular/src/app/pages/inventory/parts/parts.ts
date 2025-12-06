import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InventoryService } from '../../../services/inventory';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-parts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './parts.html',
  styleUrl: './parts.scss'
})
export class PartsComponent {
  private inventoryService = inject(InventoryService);
  parts = toSignal(this.inventoryService.getParts(), { initialValue: [] });
}

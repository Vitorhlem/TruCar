import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InventoryService } from '../../../services/inventory';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-inventory-items',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './inventory-items.html',
  styleUrl: './inventory-items.scss'
})
export class InventoryItemsComponent {
  private inventoryService = inject(InventoryService);
  items = toSignal(this.inventoryService.getInventoryItems(), { initialValue: [] });
}

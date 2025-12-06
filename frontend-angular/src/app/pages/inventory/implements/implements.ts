import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InventoryService } from '../../../services/inventory';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-implements',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './implements.html',
  styleUrl: './implements.scss'
})
export class ImplementsComponent {
  private inventoryService = inject(InventoryService);
  implements = toSignal(this.inventoryService.getImplements(), { initialValue: [] });
}

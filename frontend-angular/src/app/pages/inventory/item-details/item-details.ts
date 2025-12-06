import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InventoryService } from '../../../services/inventory';
import { toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-item-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './item-details.html',
  styleUrl: './item-details.scss'
})
export class ItemDetailsComponent {
  private route = inject(ActivatedRoute);
  private inventoryService = inject(InventoryService);

  item = toSignal(
    this.route.paramMap.pipe(
      switchMap(params => this.inventoryService.getItemById(params.get('id')!))
    )
  );
}

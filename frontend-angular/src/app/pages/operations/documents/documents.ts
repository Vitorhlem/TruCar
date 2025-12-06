import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OperationsService } from '../../../services/operations';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './documents.html',
  styleUrl: './documents.scss'
})
export class DocumentsComponent {
  private operationsService = inject(OperationsService);
  documents = toSignal(this.operationsService.getDocuments(), { initialValue: [] });
}

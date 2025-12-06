import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-user-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './user-details.html',
  styleUrl: './user-details.scss'
})
export class UserDetailsComponent {
  private route = inject(ActivatedRoute);
  userId = toSignal(this.route.paramMap.pipe(map(params => params.get('id'))));
}

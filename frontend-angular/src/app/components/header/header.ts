import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.scss'
})
export class HeaderComponent {
  // Placeholder for user info
  user = {
    name: 'Vitor',
    avatar: 'https://ui-avatars.com/api/?name=Vitor&background=0D8ABC&color=fff'
  };
}

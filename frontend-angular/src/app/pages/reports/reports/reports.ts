import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reports.html',
  styleUrl: './reports.scss'
})
export class ReportsComponent {
  reports = [
    { name: 'Monthly Fleet Summary', type: 'PDF', date: new Date() },
    { name: 'Driver Performance Review', type: 'Excel', date: new Date(Date.now() - 86400000) },
  ];
}

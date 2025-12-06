import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class DashboardComponent {
  stats = signal([
    { label: 'Total Vehicles', value: '124', icon: 'directions_car', color: 'bg-blue-500', trend: '+12%' },
    { label: 'Active Drivers', value: '45', icon: 'person', color: 'bg-green-500', trend: '+5%' },
    { label: 'Fuel Cost (Mo)', value: 'R$ 45.2k', icon: 'local_gas_station', color: 'bg-orange-500', trend: '-2%' },
    { label: 'Maintenance', value: '3', icon: 'build', color: 'bg-red-500', trend: 'Alert' },
  ]);

  recentActivity = signal([
    { title: 'Vehicle ABC-1234 started journey', time: '10 mins ago', type: 'info' },
    { title: 'Fuel refill for XYZ-9876', time: '45 mins ago', type: 'success' },
    { title: 'Maintenance alert: Brake check needed', time: '2 hours ago', type: 'warning' },
    { title: 'Driver John Doe clocked out', time: '4 hours ago', type: 'info' },
  ]);
}

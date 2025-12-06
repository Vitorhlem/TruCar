import { Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  roles?: string[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class SidebarComponent {
  navItems = signal<NavItem[]>([
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Driver Cockpit', icon: 'steering_wheel', route: '/driver-cockpit' },
    { label: 'Live Map', icon: 'map', route: '/live-map' },
    { label: 'Vehicles', icon: 'directions_car', route: '/vehicles' },
    { label: 'Maintenance', icon: 'build', route: '/maintenance' },
    { label: 'Fuel Logs', icon: 'local_gas_station', route: '/fuel-logs' },
    { label: 'Journeys', icon: 'route', route: '/journeys' },
    { label: 'Fines', icon: 'gavel', route: '/fines' },
    { label: 'Documents', icon: 'description', route: '/documents' },
    { label: 'Parts', icon: 'settings_input_component', route: '/parts' },
    { label: 'Inventory', icon: 'inventory', route: '/inventory-items' },
    { label: 'Costs', icon: 'attach_money', route: '/costs' },
    { label: 'Reports', icon: 'assessment', route: '/reports' },
    { label: 'Performance', icon: 'speed', route: '/performance' },
    { label: 'Users', icon: 'people', route: '/users' },
    { label: 'Clients', icon: 'business', route: '/clients' },
    { label: 'Freight Orders', icon: 'local_shipping', route: '/freight-orders' },
    { label: 'Implements', icon: 'handyman', route: '/implements' },
    { label: 'Feedback', icon: 'feedback', route: '/feedback' },
    { label: 'Settings', icon: 'settings', route: '/settings' },
    { label: 'Admin', icon: 'admin_panel_settings', route: '/admin' },
  ]);
}

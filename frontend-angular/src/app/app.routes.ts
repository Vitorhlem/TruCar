import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layouts/main-layout/main-layout';
import { AuthLayoutComponent } from './layouts/auth-layout/auth-layout';

export const routes: Routes = [
    {
        path: '',
        component: MainLayoutComponent,
        children: [
            { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
            {
                path: 'dashboard',
                loadComponent: () => import('./pages/dashboard/dashboard').then(m => m.DashboardComponent)
            },
            {
                path: 'driver-cockpit',
                loadComponent: () => import('./pages/driver/driver-cockpit/driver-cockpit').then(m => m.DriverCockpitComponent)
            },
            {
                path: 'journeys',
                loadComponent: () => import('./pages/driver/journeys/journeys').then(m => m.JourneysComponent)
            },
            {
                path: 'fuel-logs',
                loadComponent: () => import('./pages/driver/fuel-logs/fuel-logs').then(m => m.FuelLogsComponent)
            },
            {
                path: 'fines',
                loadComponent: () => import('./pages/driver/fines/fines').then(m => m.FinesComponent)
            },
            {
                path: 'maintenance',
                loadComponent: () => import('./pages/driver/maintenance/maintenance').then(m => m.MaintenanceComponent)
            },
            {
                path: 'vehicles',
                loadComponent: () => import('./pages/vehicles/vehicles/vehicles').then(m => m.VehiclesComponent)
            },
            {
                path: 'vehicles/:id',
                loadComponent: () => import('./pages/vehicles/vehicle-details/vehicle-details').then(m => m.VehicleDetailsComponent)
            },
            {
                path: 'users',
                loadComponent: () => import('./pages/admin/users/users').then(m => m.UsersComponent)
            },
            {
                path: 'settings',
                loadComponent: () => import('./pages/admin/settings/settings').then(m => m.SettingsComponent)
            },
            // Inventory
            { path: 'parts', loadComponent: () => import('./pages/inventory/parts/parts').then(m => m.PartsComponent) },
            { path: 'inventory-items', loadComponent: () => import('./pages/inventory/inventory-items/inventory-items').then(m => m.InventoryItemsComponent) },
            { path: 'inventory/item/:id', loadComponent: () => import('./pages/inventory/item-details/item-details').then(m => m.ItemDetailsComponent) },
            { path: 'implements', loadComponent: () => import('./pages/inventory/implements/implements').then(m => m.ImplementsComponent) },
            // Operations
            { path: 'map', loadComponent: () => import('./pages/operations/map/map').then(m => m.MapComponent) },
            { path: 'live-map', loadComponent: () => import('./pages/operations/live-map/live-map').then(m => m.LiveMapComponent) },
            { path: 'freight-orders', loadComponent: () => import('./pages/operations/freight-orders/freight-orders').then(m => m.FreightOrdersComponent) },
            { path: 'clients', loadComponent: () => import('./pages/operations/clients/clients').then(m => m.ClientsComponent) },
            { path: 'documents', loadComponent: () => import('./pages/operations/documents/documents').then(m => m.DocumentsComponent) },
            // Reports
            { path: 'performance', loadComponent: () => import('./pages/reports/performance/performance').then(m => m.PerformanceComponent) },
            { path: 'reports', loadComponent: () => import('./pages/reports/reports/reports').then(m => m.ReportsComponent) },
            { path: 'costs', loadComponent: () => import('./pages/reports/costs/costs').then(m => m.CostsComponent) },
            { path: 'audit-logs', loadComponent: () => import('./pages/reports/audit-logs/audit-logs').then(m => m.AuditLogsComponent) },
            // Other
            { path: 'feedback', loadComponent: () => import('./pages/feedback/feedback').then(m => m.FeedbackComponent) },
            { path: 'users/:id/stats', loadComponent: () => import('./pages/users/user-details/user-details').then(m => m.UserDetailsComponent) },
            { path: 'admin', loadComponent: () => import('./pages/admin/admin-dashboard/admin-dashboard').then(m => m.AdminDashboardComponent) },
        ]
    },
    {
        path: 'auth',
        component: AuthLayoutComponent,
        children: [
            { path: 'login', loadComponent: () => import('./pages/auth/login/login').then(m => m.LoginComponent) },
            { path: 'register', loadComponent: () => import('./pages/auth/register/register').then(m => m.RegisterComponent) },
            { path: 'forgot-password', loadComponent: () => import('./pages/auth/forgot-password/forgot-password').then(m => m.ForgotPasswordComponent) },
            { path: 'reset-password', loadComponent: () => import('./pages/auth/reset-password/reset-password').then(m => m.ResetPasswordComponent) },
            { path: '', redirectTo: 'login', pathMatch: 'full' }
        ]
    },
    { path: '**', redirectTo: 'dashboard' }
];

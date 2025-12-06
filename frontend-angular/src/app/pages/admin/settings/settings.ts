import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AdminService } from '../../../services/admin';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './settings.html',
  styleUrl: './settings.scss'
})
export class SettingsComponent {
  private adminService = inject(AdminService);
  settingsForm: FormGroup;
  saved = signal(false);

  constructor(private fb: FormBuilder) {
    this.settingsForm = this.fb.group({
      companyName: ['TruCar Logistics', Validators.required],
      email: ['admin@trucar.com', [Validators.required, Validators.email]],
      notifications: [true],
      darkMode: [false],
      language: ['en']
    });

    // In a real app, we would load settings here
    // this.adminService.getSettings().subscribe(settings => this.settingsForm.patchValue(settings));
  }

  saveSettings() {
    if (this.settingsForm.valid) {
      // this.adminService.updateSettings(this.settingsForm.value).subscribe(() => {
      console.log('Settings saved:', this.settingsForm.value);
      this.saved.set(true);
      setTimeout(() => this.saved.set(false), 3000);
      // });
    }
  }
}

import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.scss'
})
export class ResetPasswordComponent {
  resetForm: FormGroup;
  isLoading = signal(false);
  success = signal(false);

  constructor(private fb: FormBuilder) {
    this.resetForm = this.fb.group({
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.resetForm.valid) {
      this.isLoading.set(true);
      console.log('Reset Password:', this.resetForm.value);
      setTimeout(() => {
        this.isLoading.set(false);
        this.success.set(true);
      }, 2000);
    }
  }
}

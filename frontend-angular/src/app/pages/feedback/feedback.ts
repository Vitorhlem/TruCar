import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-feedback',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './feedback.html',
  styleUrl: './feedback.scss'
})
export class FeedbackComponent {
  feedbackForm: FormGroup;
  sent = signal(false);

  constructor(private fb: FormBuilder) {
    this.feedbackForm = this.fb.group({
      type: ['bug', Validators.required],
      message: ['', [Validators.required, Validators.minLength(10)]],
      rating: [5]
    });
  }

  onSubmit() {
    if (this.feedbackForm.valid) {
      console.log('Feedback:', this.feedbackForm.value);
      this.sent.set(true);
      setTimeout(() => this.sent.set(false), 3000);
      this.feedbackForm.reset({ type: 'bug', rating: 5 });
    }
  }
}

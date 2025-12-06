import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { tap } from 'rxjs/operators';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = `${environment.apiUrl}/login`;

  currentUser = signal<User | null>(null);

  constructor() {
    this.loadUser();
  }

  login(credentials: any) {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    return this.http.post<AuthResponse>(`${this.apiUrl}/access-token`, formData).pipe(
      tap(response => {
        this.setToken(response.access_token);
        this.loadUser(); // In a real app, you might decode the token or fetch user profile here
        // For now, let's just simulate fetching user profile or decoding token
        // Since the backend returns just the token, we might need a /users/me endpoint
        this.fetchUserProfile().subscribe();
      })
    );
  }

  register(data: any) {
    // Note: The backend might not have a public register endpoint enabled by default depending on config
    // But assuming /users/open or similar exists, or using the /login/test-token for testing
    // For this implementation, we will assume a standard register flow if available, 
    // or just use login for now as per backend structure analysis (login endpoints exist)
    return this.http.post(`${environment.apiUrl}/users/open`, data);
  }

  logout() {
    localStorage.removeItem('token');
    this.currentUser.set(null);
    this.router.navigate(['/auth/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  private setToken(token: string) {
    localStorage.setItem('token', token);
  }

  private loadUser() {
    const token = this.getToken();
    if (token) {
      this.fetchUserProfile().subscribe();
    }
  }

  private fetchUserProfile() {
    return this.http.get<User>(`${environment.apiUrl}/users/me`).pipe(
      tap(user => this.currentUser.set(user)),
      tap({ error: () => this.logout() }) // Logout if token is invalid
    );
  }
}

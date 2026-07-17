import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private toasts = signal<Toast[]>([]);
  toasts$ = this.toasts.asReadonly();
  private idCounter = 0;

  success(message: string, duration = 3000) {
    this.show(message, 'success', duration);
  }

  error(message: string, duration = 4000) {
    this.show(message, 'error', duration);
  }

  info(message: string, duration = 3000) {
    this.show(message, 'info', duration);
  }

  warning(message: string, duration = 3500) {
    this.show(message, 'warning', duration);
  }

  private show(message: string, type: Toast['type'], duration: number) {
    const id = `toast-${++this.idCounter}`;
    const toast: Toast = { id, message, type, duration };

    this.toasts.update(prev => [...prev, toast]);

    if (duration > 0) {
      setTimeout(() => this.remove(id), duration);
    }
  }

  remove(id: string) {
    this.toasts.update(prev => prev.filter(t => t.id !== id));
  }

  clear() {
    this.toasts.set([]);
  }
}

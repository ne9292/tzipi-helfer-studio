import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api';
import { ToastService } from '../../services/toast.service';
import { Client, Registration, Payment } from '../../models/models';

@Component({
  selector: 'app-clients',
  imports: [CommonModule, FormsModule],
  templateUrl: './clients.html',
  styleUrl: './clients.scss',
})
export class Clients implements OnInit {
  clients: Client[] = [];
  filtered: Client[] = [];
  search = '';

  showFormModal = false;
  showDetailModal = false;
  editMode = false;
  selectedClient: Client | null = null;
  clientRegistrations: Registration[] = [];
  clientPayments: Payment[] = [];

  form: Partial<Client> = {};
  paymentForm = { amount: 0, description: '' };

  // הוספנו את ChangeDetectorRef
  constructor(private api: ApiService, private toast: ToastService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadClients();
  }

  loadClients() {
    this.api.getClients().subscribe(c => {
      this.clients = c;
      this.applyFilter();
      this.cdr.detectChanges(); // ריענון התצוגה
    });
  }

  applyFilter() {
    const q = this.search.toLowerCase();
    this.filtered = this.clients.filter(
      c =>
        c.first_name.toLowerCase().includes(q) ||
        c.last_name.toLowerCase().includes(q) ||
        c.email.toLowerCase().includes(q) ||
        (c.phone || '').includes(q)
    );
  }



  openNew() {
    this.editMode = false;
    this.form = { active: true, payment_method: 'CASH' }; 
    this.showFormModal = true;
  }

  openEdit(client: Client) {
    this.editMode = true;
    this.form = { ...client };
    this.showFormModal = true;
  }

  saveClient() {
    const obs = this.editMode && this.form.id
      ? this.api.updateClient(this.form.id, this.form)
      : this.api.createClient(this.form);
    obs.subscribe(() => {
      this.toast.success(this.editMode ? 'לקוחה עודכנה בהצלחה ✓' : 'לקוחה חדשה נוספה ✓');
      this.showFormModal = false;
      this.loadClients();
    });
  }

  openDetail(client: Client) {
    this.selectedClient = client;
    this.showDetailModal = true;
    
    this.api.getClientRegistrations(client.id).subscribe(r => {
      this.clientRegistrations = r;
      this.cdr.detectChanges(); // ריענון אחרי קבלת הרשמות
    });
    
    this.api.getClientPayments(client.id).subscribe(p => {
      this.clientPayments = p;
      this.cdr.detectChanges(); // ריענון אחרי קבלת תשלומים
    });
  }

  toggleActive(client: Client) {
    this.api.updateClient(client.id, { active: !client.active }).subscribe(() => {
      this.toast.success(client.active ? 'לקוחה השתהתה' : 'לקוחה הופעלה');
      this.loadClients();
    });
  }

  deleteClient(client: Client) {
    if (!confirm(`למחוק את ${client.first_name} ${client.last_name}?`)) return;
    this.api.deleteClient(client.id).subscribe(() => {
      this.toast.success('לקוחה נמחקה');
      this.loadClients();
    });
  }

  addPayment() {
    if (!this.selectedClient || !this.paymentForm.amount) return;
    this.api.createPayment({
      client_id: this.selectedClient.id,
      amount: this.paymentForm.amount,
      description: this.paymentForm.description,
    }).subscribe(p => {
      this.toast.success('תשלום נוסף ✓');
      this.clientPayments.unshift(p);
      this.paymentForm = { amount: 0, description: '' };
      this.cdr.detectChanges();
    });
  }

  markPaid(payment: Payment) {
    this.api.markPaid(payment.id).subscribe(updated => {
      this.toast.success('תשלום סומן כשולם ✓');
      const i = this.clientPayments.findIndex(p => p.id === payment.id);
      if (i >= 0) {
        this.clientPayments[i] = updated;
        this.cdr.detectChanges();
      }
    });
  }

  totalDebt(): number {
    return this.clientPayments
      .filter(p => p.status !== 'paid')
      .reduce((s, p) => s + p.amount, 0);
  }

  formatDate(iso?: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('he-IL');
  }

  initials(client: Client): string {
    return ((client.first_name[0] ?? '') + (client.last_name[0] ?? '')).toUpperCase();
  }

  avatarColor(client: Client): string {
    const palette = ['#6366f1','#8b5cf6','#ec4899','#06b6d4','#10b981','#f59e0b','#ef4444'];
    const idx = ((client.first_name.charCodeAt(0) ?? 0) + (client.last_name.charCodeAt(0) ?? 0)) % palette.length;
    return palette[idx];
  }
}
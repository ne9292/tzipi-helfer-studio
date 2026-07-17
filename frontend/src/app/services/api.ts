import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Client, Session, Registration, Payment, DashboardStats, SessionType } from '../models/models';

const BASE = 'http://localhost:8000/api';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  // Clients
  getClients(activeOnly = false): Observable<Client[]> {
    return this.http.get<Client[]>(`${BASE}/clients`, {
      params: activeOnly ? { active_only: 'true' } : {},
    });
  }
  getClient(id: number): Observable<Client> {
    return this.http.get<Client>(`${BASE}/clients/${id}`);
  }
  createClient(data: Partial<Client>): Observable<Client> {
    return this.http.post<Client>(`${BASE}/clients`, data);
  }
  updateClient(id: number, data: Partial<Client>): Observable<Client> {
    return this.http.patch<Client>(`${BASE}/clients/${id}`, data);
  }
  deleteClient(id: number): Observable<any> {
    return this.http.delete(`${BASE}/clients/${id}`);
  }
  getClientRegistrations(id: number): Observable<Registration[]> {
    return this.http.get<Registration[]>(`${BASE}/clients/${id}/registrations`);
  }
  getClientPayments(id: number): Observable<Payment[]> {
    return this.http.get<Payment[]>(`${BASE}/clients/${id}/payments`);
  }

  // Sessions
  getSessions(params?: { start?: string; end?: string; session_type?: SessionType }): Observable<Session[]> {
    let p = new HttpParams();
    if (params?.start) p = p.set('start', params.start);
    if (params?.end) p = p.set('end', params.end);
    if (params?.session_type) p = p.set('session_type', params.session_type);
    return this.http.get<Session[]>(`${BASE}/sessions`, { params: p });
  }
  getSession(id: number): Observable<Session> {
    return this.http.get<Session>(`${BASE}/sessions/${id}`);
  }
  createSession(data: Partial<Session>): Observable<Session> {
    return this.http.post<Session>(`${BASE}/sessions`, data);
  }
  updateSession(id: number, data: Partial<Session>): Observable<Session> {
    return this.http.patch<Session>(`${BASE}/sessions/${id}`, data);
  }
  deleteSession(id: number): Observable<any> {
    return this.http.delete(`${BASE}/sessions/${id}`);
  }
  deleteRecurringSeries(id: number): Observable<any> {
    return this.http.delete(`${BASE}/sessions/${id}/series`);
  }
  getSessionRegistrations(id: number): Observable<Registration[]> {
    return this.http.get<Registration[]>(`${BASE}/sessions/${id}/registrations`);
  }
  chargeSessionClients(id: number): Observable<{ ok: boolean; charged: number }> {
    return this.http.post<{ ok: boolean; charged: number }>(`${BASE}/sessions/${id}/charge`, {});
  }

  // Registrations
  register(clientId: number, sessionId: number): Observable<Registration> {
    return this.http.post<Registration>(`${BASE}/registrations`, {
      client_id: clientId,
      session_id: sessionId,
    });
  }
  updateAttendance(regId: number, attended: boolean): Observable<Registration> {
    return this.http.patch<Registration>(`${BASE}/registrations/${regId}/attendance`, { attended });
  }
  cancelRegistration(regId: number): Observable<any> {
    return this.http.delete(`${BASE}/registrations/${regId}`);
  }

  // Payments
  getPayments(clientId?: number): Observable<Payment[]> {
    let p = new HttpParams();
    if (clientId != null) p = p.set('client_id', String(clientId));
    return this.http.get<Payment[]>(`${BASE}/payments`, { params: p });
  }
  createPayment(data: Partial<Payment>): Observable<Payment> {
    return this.http.post<Payment>(`${BASE}/payments`, data);
  }
  markPaid(id: number): Observable<Payment> {
    return this.http.patch<Payment>(`${BASE}/payments/${id}/pay`, {});
  }

  // Dashboard
  getDashboard(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${BASE}/dashboard`);
  }
}

import { Component, OnInit, signal, NgZone, ChangeDetectorRef } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FullCalendarModule } from '@fullcalendar/angular';
import { CalendarOptions, EventClickArg, DateSelectArg, EventContentArg } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import heLocale from '@fullcalendar/core/locales/he';
import { ApiService } from '../../services/api';
import { ToastService } from '../../services/toast.service';
import { Session, Client, Registration } from '../../models/models';

@Component({
  selector: 'app-calendar',
  standalone: true,
  imports: [CommonModule, FormsModule, FullCalendarModule, DatePipe],
  templateUrl: './calendar.html',
  styleUrl: './calendar.scss',
})
export class Calendar implements OnInit {
  sessions: Session[] = [];
  clients: Client[] = [];
  registrations: Registration[] = [];

  showSessionModal = false;
  showDetailModal = false;
  editMode = false;
  selectedSession: Session | null = null;
  conflictName: string | null = null;
  saveLoading = false;

  // משתני מצב חדשים לניהול ה-Dropdown והסינון של 100+ תלמידות
  showClientsDropdown = false;
  clientSearchTerm = '';

  form = {
    title: '',
    session_type: 'group' as 'group' | 'private',
    start_time: '',
    duration_minutes: 45,
    max_capacity: 10,
    price_per_month: 0,
    location: '',
    notes: '',
    is_recurring: false,
    weeks_ahead: 52,
    selected_client_ids: [] as number[]
  };

  calendarOptions = signal<CalendarOptions>({
    plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
    initialView: 'timeGridWeek',
    locale: heLocale,
    direction: 'rtl',
    headerToolbar: {
      right: 'prev,next today',
      center: 'title',
      left: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
    },
    buttonText: {
      today: 'היום',
      month: 'חודש',
      week: 'שבוע',
      day: 'יום',
      list: 'רשימה',
    },
    slotMinTime: '06:00:00',
    slotMaxTime: '23:00:00',
    slotDuration: '00:15:00',
    slotLabelInterval: '01:00',
    slotLabelFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
    selectable: true,
    selectMirror: true,
    editable: false,
    nowIndicator: true,
    allDaySlot: false,
    expandRows: true,
    events: [],
    eventContent: (arg: EventContentArg) => this.renderEvent(arg),
    select: (arg: DateSelectArg) => this.onDateSelect(arg),
    eventClick: (arg: EventClickArg) => this.onEventClick(arg),
  });

  constructor(
    private api: ApiService, 
    private toast: ToastService,
    private zone: NgZone,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadSessions();
    this.api.getClients().subscribe(c => {
      this.clients = c;
      this.cdr.detectChanges();
    });
  }

  // פונקציית סינון דינמית המופעלת על רשימת הלקוחות לפי ערך החיפוש
  filteredClients(): Client[] {
    const term = this.clientSearchTerm.toLowerCase().trim();
    if (!term) {
      return this.clients;
    }
    return this.clients.filter(c => 
      `${c.first_name} ${c.last_name}`.toLowerCase().includes(term)
    );
  }

  // שליפת אובייקט הלקוחה לפי מזהה כדי להציג את השם שלה בצ'יפים החיצוניים
  getClientById(clientId: number): Client | undefined {
    return this.clients.find(c => c.id === clientId);
  }

  isClientSelected(clientId: number): boolean {
    if (!this.form.selected_client_ids) this.form.selected_client_ids = [];
    return this.form.selected_client_ids.includes(clientId);
  }

  toggleClientSelection(clientId: number): void {
    if (!this.form.selected_client_ids) this.form.selected_client_ids = [];
    
    const index = this.form.selected_client_ids.indexOf(clientId);
    if (index > -1) {
      this.form.selected_client_ids.splice(index, 1);
    } else {
      if (this.form.session_type === 'group' && this.form.selected_client_ids.length >= (this.form.max_capacity || 0)) {
        return; 
      }
      this.form.selected_client_ids.push(clientId);
    }
    this.cdr.detectChanges();
  }

  private renderEvent(arg: EventContentArg): { html: string } {
    const p = arg.event.extendedProps;
    const isPrivate = p['sessionType'] === 'private';
    const reg: number = p['registeredCount'] ?? 0;
    const max: number = p['maxCapacity'] ?? 0;
    const full = !isPrivate && max > 0 && reg >= max;
    const pct = max > 0 ? Math.min((reg / max) * 100, 100) : 0;
    const isRecurring: boolean = p['isRecurring'] ?? false;

    const capacityHtml = isPrivate
      ? `<div class="ev-type-tag">🔒 פרטי</div>`
      : `<div class="ev-cap-row">
           <div class="ev-cap-track"><div class="ev-cap-fill${full ? ' full' : ''}" style="width:${pct}%"></div></div>
           <span class="ev-cap-num${full ? ' full' : ''}">${reg}/${max}</span>
         </div>`;

    return {
      html: `<div class="ev-card">
               <div class="ev-title-row">
                 <span class="ev-title">${arg.event.title}</span>
                 ${isRecurring ? '<span class="ev-recur-dot" title="שיעור קבוע"></span>' : ''}
               </div>
               ${capacityHtml}
             </div>`
    };
  }

  loadSessions() {
    this.api.getSessions().subscribe(sessions => {
      this.sessions = sessions;
      this.calendarOptions.update(opts => ({
        ...opts,
        events: sessions.map(s => ({
          id: String(s.id),
          title: s.title,
          start: s.start_time,
          end: this.addMinutes(s.start_time, s.duration_minutes),
          color: s.session_type === 'private' ? '#f97316' : '#6366f1',
          extendedProps: {
            sessionId: s.id,
            sessionType: s.session_type,
            registeredCount: s.registered_count,
            maxCapacity: s.max_capacity,
            isRecurring: s.is_recurring,
            location: s.location,
          },
        })),
      }));
      this.cdr.detectChanges();
    });
  }

  onDateSelect(arg: DateSelectArg) {
    this.zone.run(() => {
      this.editMode = false;
      this.conflictName = null;
      this.showClientsDropdown = false;
      this.clientSearchTerm = '';
      this.form = {
        title: '',
        session_type: 'group',
        start_time: this.toLocalInput(arg.start),
        duration_minutes: 45,
        max_capacity: 10,
        price_per_month: 0,
        location: '',
        notes: '',
        is_recurring: false,
        weeks_ahead: 52,
        selected_client_ids: []
      };
      this.showSessionModal = true;
      this.cdr.detectChanges();
    });
  }

  onEventClick(arg: EventClickArg) {
    this.zone.run(() => {
      const id = Number(arg.event.extendedProps['sessionId']);
      this.selectedSession = this.sessions.find(s => s.id === id) || null;
      if (!this.selectedSession) return;
      
      this.api.getSessionRegistrations(id).subscribe(r => {
        this.registrations = r;
        this.showDetailModal = true;
        this.cdr.detectChanges();
      });
    });
  }

  openNew() {
    this.editMode = false;
    this.conflictName = null;
    this.showClientsDropdown = false;
    this.clientSearchTerm = '';
    this.form = {
      title: '', session_type: 'group', start_time: '',
      duration_minutes: 45, max_capacity: 10, price_per_month: 0,
      location: '', notes: '', is_recurring: false, weeks_ahead: 52,
      selected_client_ids: []
    };
    this.showSessionModal = true;
  }

  openEdit() {
    if (!this.selectedSession) return;
    const s = this.selectedSession;
    this.conflictName = null;
    this.showClientsDropdown = false;
    this.clientSearchTerm = '';
    
    this.form = {
      title: s.title,
      session_type: s.session_type,
      start_time: this.toLocalInput(new Date(s.start_time)),
      duration_minutes: s.duration_minutes,
      max_capacity: s.max_capacity,
      price_per_month: s.price_per_month ?? 0,
      location: s.location || '',
      notes: s.notes || '',
      is_recurring: s.is_recurring,
      weeks_ahead: 52,
      selected_client_ids: this.registrations.map(r => r.client_id)
    };
    this.editMode = true;
    this.showDetailModal = false;
    this.showSessionModal = true;
  }

  saveSession() {
    const localIso = this.form.start_time.length === 16
      ? this.form.start_time + ':00'
      : this.form.start_time;

    const newStart = new Date(this.form.start_time);
    const newEnd = new Date(newStart.getTime() + this.form.duration_minutes * 60_000);
    const conflict = this.sessions.find(s => {
      if (this.editMode && s.id === this.selectedSession?.id) return false;
      const sStart = new Date(s.start_time);
      const sEnd = new Date(sStart.getTime() + s.duration_minutes * 60_000);
      return newStart < sEnd && newEnd > sStart;
    });
    
    if (conflict) { this.conflictName = conflict.title; return; }
    this.conflictName = null;

    this.saveLoading = true;
    const payload: any = {
      title: this.form.title,
      session_type: this.form.session_type,
      start_time: localIso,
      duration_minutes: this.form.duration_minutes,
      max_capacity: this.form.max_capacity,
      price_per_month: this.form.price_per_month,
      location: this.form.location,
      notes: this.form.notes,
      is_recurring: this.form.is_recurring,
      weeks_ahead: this.form.weeks_ahead,
      client_ids: this.form.selected_client_ids
    };

    const obs = this.editMode && this.selectedSession
      ? this.api.updateSession(this.selectedSession.id, payload)
      : this.api.createSession(payload);

    obs.subscribe({
      next: () => {
        this.toast.success(this.editMode ? 'שיעור עודכן ✓' : (this.form.is_recurring ? 'סדרת שיעורים נוצרה ✓' : 'שיעור נוסף ✓'));
        this.showSessionModal = false;
        this.saveLoading = false;
        this.loadSessions();
      },
      error: () => { 
        this.saveLoading = false; 
        this.cdr.detectChanges();
      }
    });
  }

  deleteSession() {
    if (!this.selectedSession) return;
    if (!confirm(`למחוק את השיעור "${this.selectedSession.title}"?\nפעולה זו לא ניתנת לביטול.`)) return;
    this.api.deleteSession(this.selectedSession.id).subscribe(() => {
      this.toast.success('שיעור נמחק');
      this.showDetailModal = false;
      this.loadSessions();
    });
  }

  deleteAllFuture() {
    if (!this.selectedSession) return;
    const msg = `ביטול סדרת השיעורים הקבועים של "${this.selectedSession.title}".\n\nכל השיעורים מהיום ואילך יימחקו.\nרוצה להמשיך?`;
    if (!confirm(msg)) return;
    this.api.deleteRecurringSeries(this.selectedSession.id).subscribe({
      next: (res) => {
        this.toast.success(`סדרה בוטלה - ${res.deleted} שיעורים נמחקו`);
        this.showDetailModal = false;
        this.loadSessions();
      },
      error: () => this.deleteSession()
    });
  }

  registerClient(clientId: number) {
    if (!this.selectedSession) return;
    this.api.register(clientId, this.selectedSession.id).subscribe({
      next: () => {
        this.toast.success('לקוחה נרשמה ✓');
        this.api.getSessionRegistrations(this.selectedSession!.id).subscribe(r => {
          this.registrations = r; 
          this.loadSessions();
        });
      },
      error: err => {
        if (err.error?.detail === 'already_registered') {
          this.toast.warning('לקוחה זו כבר רשומה לשיעור');
        }
      },
    });
  }

  removeRegistration(regId: number) {
    if (!confirm('להסיר לקוחה זו מהשיעור?')) return;
    this.api.cancelRegistration(regId).subscribe(() => {
      this.toast.success('הרשמה בוטלה');
      this.registrations = this.registrations.filter(r => r.id !== regId);
      this.loadSessions();
    });
  }

  toggleAttendance(reg: Registration) {
    this.api.updateAttendance(reg.id, !reg.attended).subscribe(updated => {
      this.toast.success(updated.attended ? 'נוכחות סומנה ✓' : 'נוכחות בוטלה');
      const i = this.registrations.findIndex(r => r.id === reg.id);
      if (i >= 0) {
        this.registrations[i] = { ...updated };
        this.cdr.detectChanges();
      }
    });
  }

  unregisteredClients(): Client[] {
    const registered = new Set(this.registrations.map(r => r.client_id));
    return this.clients.filter(c => !registered.has(c.id) && c.active);
  }

  recurringPreview(): string {
    if (!this.form.start_time || !this.form.is_recurring) return '';
    const start = new Date(this.form.start_time);
    const end = new Date(start);
    end.setDate(end.getDate() + this.form.weeks_ahead * 7);
    const fmt = (d: Date) => d.toLocaleDateString('he-IL', { day: 'numeric', month: 'long' });
    return `ייווצרו ${this.form.weeks_ahead} שיעורים: ${fmt(start)} – ${fmt(end)}`;
  }

  chargeClients() {
    if (!this.selectedSession) return;
    const name = this.selectedSession.title;
    const price = this.selectedSession.price_per_month;
    if (!confirm(`לחייב את כל הנרשמות לשיעור "${name}" — ₪${price} לכל לקוחה?`)) return;
    this.api.chargeSessionClients(this.selectedSession.id).subscribe({
      next: res => alert(`✓ נוצרו ${res.charged} חיובים`),
      error: () => alert('שגיאה ביצירת החיובים'),
    });
  }

  private addMinutes(iso: string, mins: number): string {
    const d = new Date(iso);
    d.setMinutes(d.getMinutes() + mins);
    return d.toISOString();
  }

  private toLocalInput(d: Date): string {
    const p = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
  }
}
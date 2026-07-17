export type SessionType = 'group' | 'private';
export type PaymentStatus = 'paid' | 'pending' | 'partial';
export type PaymentMethod = 'CASH' | 'TRANSFER' | 'STANDING_ORDER';

export interface Client {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  notes?: string;
  active: boolean;
  created_at?: string;
  payment_method?: PaymentMethod;
}

export interface Session {
  id: number;
  title: string;
  session_type: SessionType;
  start_time: string;
  duration_minutes: number;
  max_capacity: number;
  location?: string;
  notes?: string;
  is_recurring: boolean;
  recurrence_rule?: string;
  recurrence_group_id?: string;
  reminder_sent: boolean;
  registered_count: number;
  available_spots: number;
  price_per_month: number;
}

export interface Registration {
  id: number;
  client_id: number;
  session_id: number;
  registered_at?: string;
  attended?: boolean;
  on_waitlist: boolean;
  client?: Client;
  session?: Session;
}

export interface Payment {
  id: number;
  client_id: number;
  amount: number;
  status: PaymentStatus;
  description?: string;
  paid_at?: string;
  created_at?: string;
  client?: Client;
}

export interface DashboardStats {
  today_sessions: number;
  today_clients: number;
  total_active_clients: number;
  monthly_revenue: number;
  upcoming_sessions: Session[];
}

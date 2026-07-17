import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { Calendar } from './components/calendar/calendar';
import { Clients } from './components/clients/clients';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: Dashboard },
  { path: 'calendar', component: Calendar },
  { path: 'clients', component: Clients },
];

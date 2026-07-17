import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ToastService } from './toast.service';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(private toast: ToastService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'שגיאה בלתי צפויה';

        if (error.error instanceof ErrorEvent) {
          // Client-side error
          errorMessage = `שגיאה: ${error.error.message}`;
        } else {
          // Server-side error
          if (error.status === 0) {
            errorMessage = 'לא ניתן להתחבר לשרת - בדקי חיבור אינטרנט';
          } else if (error.status === 400) {
            errorMessage = error.error?.detail || 'בקשה שגויה';
          } else if (error.status === 404) {
            errorMessage = 'הנתון לא נמצא';
          } else if (error.status === 409) {
            errorMessage = error.error?.detail || 'נתון כזה כבר קיים';
          } else if (error.status === 422) {
            errorMessage = error.error?.detail || 'בדקי את הנתונים שהכנסת';
          } else if (error.status === 500) {
            errorMessage = 'שגיאת שרת - יצור קשר עם התמיכה';
          } else if (error.status >= 500) {
            errorMessage = 'בעיה בשרת - נא נסי שוב מאוחר יותר';
          }
        }

        this.toast.error(errorMessage);
        return throwError(() => error);
      })
    );
  }
}

# הרצת המערכת

## דרישות מוקדמות
- Python 3.11+
- Node.js 18+
- PostgreSQL מותקן ורץ

---

## 1. הגדרת מסד הנתונים (PostgreSQL)

```sql
CREATE DATABASE fitness_studio;
```

---

## 2. הגדרת הבאקאנד

```bash
cd backend

# העתק והגדר משתני סביבה
copy .env.example .env
# ערוך את .env והכנס פרטי Gmail (אופציונלי - תזכורות דורשות זה)

# התקן תלויות
pip install -r requirements.txt

# הרץ
python -m uvicorn main:app --reload --port 8000
```

הבאקאנד יהיה זמין בכתובת: http://localhost:8000
תיעוד API (Swagger): http://localhost:8000/docs

### אפשרות: הוספת דוגמה נתונים

```bash
# צור לקוחות/שיעורים לדוגמה
python seed.py
```

---

## 3. הגדרת הפרונטאנד (Angular)

```bash
cd frontend
npm install
ng serve
```

האפליקציה תהיה זמינה בכתובת: http://localhost:4200

---

## הגדרת Gmail לשליחת מיילים (אופציונלי)

התזכורות מייל אוטומטיות דורשות חשבון Gmail. אם לא קיים, המערכת תעבוד בלי מיילים.

### כדי להפעיל תזכורות:

1. כנסי לחשבון Gmail של המכון
2. הפעילי אימות דו-שלבי (Two-Factor Authentication)
3. לכי ל: [Google Account → Security → App Passwords](https://myaccount.google.com/apppasswords)
4. צרי App Password חדש עבור "Mail"
5. הכניסי אותו ב-.env:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   MAIL_FROM=your-email@gmail.com
   ```

המיילים נשלחים אוטומטית כל לילה בשעה 20:00 (שעון ישראל) לכל משתתפות בשיעורים למחרת.

---

## תכונות המערכת

| תכונה | תיאור |
|-------|-------|
| 📅 יומן | לוח שנה שבועי/חודשי עם גרירה |
| 👥 שיעורי קבוצות | רישום עד N משתתפות, רשימת המתנה |
| 🏋️ שיעורים פרטיים | תיאום אישי עם לקוחה |
| 📧 תזכורות מייל | נשלחות אוטומטית ב-20:00 לפני כל שיעור |
| 👤 ניהול לקוחות | כרטיס לקוחה עם היסטוריה ותשלומים |
| 💰 תשלומים | מעקב חובות וסימון תשלומים |
| ✅ נוכחות | סימון מי הגיעה לשיעור |
| 🔄 רשימת המתנה | אוטומטית כשיש ביטול |

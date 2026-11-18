import http.server
import socketserver
import json
import sqlite3
import urllib.parse
import os
import io
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

PORT = 8000
DB_PATH = 'bar_system.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class BarAppHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.startswith('/api/'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        params = urllib.parse.parse_qs(url.query)

        if path.startswith('/api/'):
            self.handle_api_get(path, params)
        else:
            if path == '/' or path == '':
                self.path = '/index.html'
            return super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        if path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8')) if body else {}
            except Exception:
                data = {}
            self.handle_api_post(path, data)
        else:
            self.send_error(404, "Not Found")

    def do_PUT(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        if path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8')) if body else {}
            except Exception:
                data = {}
            self.handle_api_put(path, data)
        else:
            self.send_error(404, "Not Found")

    def do_DELETE(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        if path.startswith('/api/'):
            self.handle_api_delete(path)
        else:
            self.send_error(404, "Not Found")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ================= API GET HANDLERS =================
    def handle_api_get(self, path, params):
        conn = get_db()
        cur = conn.cursor()

        try:
            if path == '/api/clubs':
                cur.execute('SELECT * FROM clubs ORDER BY id')
                rows = [dict(r) for r in cur.fetchall()]
                self.send_json({'success': True, 'clubs': rows})

            elif path == '/api/dancers':
                club_id = params.get('club_id', [None])[0]
                query = '''
                    SELECT d.*, c.name as club_name, c.code as club_code
                    FROM dancers d
                    JOIN clubs c ON d.club_id = c.id
                    WHERE d.is_active = 1
                '''
                args = []
                if club_id and club_id != 'all':
                    query += ' AND d.club_id = ?'
                    args.append(club_id)
                query += ' ORDER BY d.club_id, d.stage_name COLLATE NOCASE'
                cur.execute(query, args)
                rows = [dict(r) for r in cur.fetchall()]
                self.send_json({'success': True, 'dancers': rows})

            elif path == '/api/tariffs':
                club_id = params.get('club_id', [None])[0]
                query = 'SELECT * FROM tariffs'
                args = []
                if club_id and club_id != 'all':
                    query += ' WHERE club_id = ?'
                    args.append(club_id)
                cur.execute(query, args)
                rows = [dict(r) for r in cur.fetchall()]
                self.send_json({'success': True, 'tariffs': rows})

            elif path == '/api/records':
                club_id = params.get('club_id', [None])[0]
                date = params.get('date', [None])[0]
                start_date = params.get('start_date', [None])[0]
                end_date = params.get('end_date', [None])[0]

                query = '''
                    SELECT r.*, d.stage_name, d.real_name, d.bank_account, d.dancer_type,
                           c.name as club_name, c.code as club_code
                    FROM daily_records r
                    JOIN dancers d ON r.dancer_id = d.id
                    JOIN clubs c ON r.club_id = c.id
                    WHERE 1=1
                '''
                args = []
                if club_id and club_id != 'all':
                    query += ' AND r.club_id = ?'
                    args.append(club_id)
                if date:
                    query += ' AND r.date = ?'
                    args.append(date)
                elif start_date and end_date:
                    query += ' AND r.date BETWEEN ? AND ?'
                    args.extend([start_date, end_date])

                query += ' ORDER BY r.date DESC, r.id DESC'
                cur.execute(query, args)
                rows = [dict(r) for r in cur.fetchall()]
                self.send_json({'success': True, 'records': rows})

            elif path == '/api/report':
                club_id = params.get('club_id', [None])[0]
                start_date = params.get('start_date', [None])[0]
                end_date = params.get('end_date', [None])[0]

                query = '''
                    SELECT d.id as dancer_id, d.stage_name, d.real_name, d.bank_account, d.dancer_type,
                           c.name as club_name, c.code as club_code,
                           COUNT(r.id) as shifts_count,
                           SUM(r.tip_qty) as total_tip_qty,
                           SUM(r.tip_amount) as total_tip_amount,
                           SUM(r.wine_reg_qty) as total_wine_reg_qty,
                           SUM(r.wine_reg_amount) as total_wine_reg_amount,
                           SUM(r.wine_exp_qty) as total_wine_exp_qty,
                           SUM(r.wine_exp_amount) as total_wine_exp_amount,
                           SUM(r.sit_reg_qty) as total_sit_reg_qty,
                           SUM(r.sit_reg_amount) as total_sit_reg_amount,
                           SUM(r.sit_drink_qty) as total_sit_drink_qty,
                           SUM(r.sit_drink_amount) as total_sit_drink_amount,
                           SUM(r.extra_qty) as total_extra_qty,
                           SUM(r.extra_amount) as total_extra,
                           SUM(r.penalty_amount) as total_penalty,
                           SUM(r.total_amount) as grand_total
                    FROM daily_records r
                    JOIN dancers d ON r.dancer_id = d.id
                    JOIN clubs c ON r.club_id = c.id
                    WHERE 1=1
                '''
                args = []
                if club_id and club_id != 'all':
                    query += ' AND r.club_id = ?'
                    args.append(club_id)
                if start_date and end_date:
                    query += ' AND r.date BETWEEN ? AND ?'
                    args.extend([start_date, end_date])

                query += ' GROUP BY d.id ORDER BY grand_total DESC'
                cur.execute(query, args)
                rows = [dict(r) for r in cur.fetchall()]

                # Summary metrics
                total_sum = sum(r['grand_total'] or 0 for r in rows)
                total_tips = sum(r['total_tip_qty'] or 0 for r in rows)
                total_wines_reg = sum(r['total_wine_reg_qty'] or 0 for r in rows)
                total_wines_exp = sum(r['total_wine_exp_qty'] or 0 for r in rows)
                total_sits = sum((r['total_sit_reg_qty'] or 0) + (r['total_sit_drink_qty'] or 0) for r in rows)
                total_extras = sum(r['total_extra_qty'] or 0 for r in rows)

                self.send_json({
                    'success': True,
                    'report': rows,
                    'summary': {
                        'total_sum': total_sum,
                        'total_tips': total_tips,
                        'total_wines_reg': total_wines_reg,
                        'total_wines_exp': total_wines_exp,
                        'total_wines': total_wines_reg + total_wines_exp,
                        'total_sits': total_sits,
                        'total_extras': total_extras,
                        'total_dancers': len(rows)
                    }
                })

            elif path == '/api/export/excel':
                self.handle_export_excel(params)

            else:
                self.send_error(404, "API endpoint not found")
        finally:
            conn.close()

    # ================= API POST HANDLERS =================
    def handle_api_post(self, path, data):
        conn = get_db()
        cur = conn.cursor()

        try:
            if path == '/api/dancers':
                stage_name = data.get('stage_name', '').strip()
                if not stage_name:
                    self.send_json({'success': False, 'message': 'Бүжигчний нэр хоосон байна'}, 400)
                    return

                cur.execute('''
                    INSERT INTO dancers (club_id, stage_name, real_name, bank_account, phone, dancer_type, tag)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('club_id', 1),
                    stage_name,
                    data.get('real_name', '').strip(),
                    data.get('bank_account', '').strip(),
                    data.get('phone', '').strip(),
                    data.get('dancer_type', 'Үндсэн'),
                    data.get('tag', '').strip()
                ))
                conn.commit()
                new_id = cur.lastrowid
                self.send_json({'success': True, 'id': new_id, 'message': 'Бүжигчин амжилттай нэмэгдлээ'})

            elif path == '/api/records':
                club_id = data.get('club_id')
                dancer_id = data.get('dancer_id')
                date_val = data.get('date', datetime.date.today().isoformat())

                if not club_id or not dancer_id:
                    self.send_json({'success': False, 'message': 'Салбар болон Бүжигчнийг сонгоно уу'}, 400)
                    return

                # Calculate amounts using tariffs
                cur.execute('SELECT dancer_type FROM dancers WHERE id = ?', (dancer_id,))
                d_row = cur.fetchone()
                dtype = d_row['dancer_type'] if d_row else 'Үндсэн'

                cur.execute('SELECT item_key, rate FROM tariffs WHERE club_id = ? AND dancer_type = ?', (club_id, dtype))
                rates = {r['item_key']: r['rate'] for r in cur.fetchall()}

                tip_rate = rates.get('tip', 15000)
                wine_reg_rate = rates.get('wine_reg', 100000)
                wine_exp_rate = rates.get('wine_exp', 120000)
                sit_reg_rate = rates.get('sit_reg', 70000)
                sit_drink_rate = rates.get('sit_drink', 120000)
                extra_rate = rates.get('extra', 200000)

                tip_qty = int(data.get('tip_qty', 0))
                wine_reg_qty = int(data.get('wine_reg_qty', 0))
                wine_exp_qty = int(data.get('wine_exp_qty', 0))
                sit_reg_qty = int(data.get('sit_reg_qty', 0))
                sit_drink_qty = int(data.get('sit_drink_qty', 0))
                extra_qty = int(data.get('extra_qty', 0))
                
                # Extra amount: can be (extra_qty * extra_rate) + optional manual extra
                manual_extra = int(data.get('manual_extra_amount', 0))
                extra_amount = (extra_qty * extra_rate) + manual_extra
                penalty_amount = int(data.get('penalty_amount', 0))

                tip_amount = tip_qty * tip_rate
                wine_reg_amount = wine_reg_qty * wine_reg_rate
                wine_exp_amount = wine_exp_qty * wine_exp_rate
                sit_reg_amount = sit_reg_qty * sit_reg_rate
                sit_drink_amount = sit_drink_qty * sit_drink_rate

                total_amount = tip_amount + wine_reg_amount + wine_exp_amount + sit_reg_amount + sit_drink_amount + extra_amount - penalty_amount

                cur.execute('''
                    INSERT INTO daily_records (
                        date, club_id, dancer_id, tip_qty, tip_amount,
                        wine_reg_qty, wine_reg_amount, wine_exp_qty, wine_exp_amount,
                        sit_reg_qty, sit_reg_amount, sit_drink_qty, sit_drink_amount,
                        extra_qty, extra_amount, penalty_amount, total_amount, bartender_name, note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date_val, club_id, dancer_id,
                    tip_qty, tip_amount,
                    wine_reg_qty, wine_reg_amount,
                    wine_exp_qty, wine_exp_amount,
                    sit_reg_qty, sit_reg_amount,
                    sit_drink_qty, sit_drink_amount,
                    extra_qty, extra_amount, penalty_amount, total_amount,
                    data.get('bartender_name', '').strip(),
                    data.get('note', '').strip()
                ))
                conn.commit()
                new_id = cur.lastrowid
                self.send_json({'success': True, 'id': new_id, 'total_amount': total_amount, 'message': 'Бичилт амжилттай хадгалагдлаа'})

            else:
                self.send_error(404, "API endpoint not found")
        finally:
            conn.close()

    # ================= API PUT HANDLERS =================
    def handle_api_put(self, path, data):
        conn = get_db()
        cur = conn.cursor()

        try:
            if path.startswith('/api/dancers/'):
                dancer_id = int(path.split('/')[-1])
                cur.execute('''
                    UPDATE dancers
                    SET stage_name = ?, real_name = ?, bank_account = ?, phone = ?, club_id = ?, dancer_type = ?, tag = ?
                    WHERE id = ?
                ''', (
                    data.get('stage_name', '').strip(),
                    data.get('real_name', '').strip(),
                    data.get('bank_account', '').strip(),
                    data.get('phone', '').strip(),
                    data.get('club_id'),
                    data.get('dancer_type', 'Үндсэн'),
                    data.get('tag', '').strip(),
                    dancer_id
                ))
                conn.commit()
                self.send_json({'success': True, 'message': 'Бүжигчний мэдээлэл шинэчлэгдлээ'})

            elif path == '/api/tariffs':
                # Batch update tariffs
                items = data.get('tariffs', [])
                for it in items:
                    cur.execute('''
                        UPDATE tariffs SET rate = ? WHERE id = ?
                    ''', (it['rate'], it['id']))
                conn.commit()
                self.send_json({'success': True, 'message': 'Тарифын ханш амжилттай шинэчлэгдлээ'})

            else:
                self.send_error(404, "API endpoint not found")
        finally:
            conn.close()

    # ================= API DELETE HANDLERS =================
    def handle_api_delete(self, path):
        conn = get_db()
        cur = conn.cursor()

        try:
            if path.startswith('/api/dancers/'):
                dancer_id = int(path.split('/')[-1])
                cur.execute('SELECT COUNT(*) as cnt FROM daily_records WHERE dancer_id = ?', (dancer_id,))
                cnt = cur.fetchone()['cnt']
                if cnt > 0:
                    cur.execute('UPDATE dancers SET is_active = 0 WHERE id = ?', (dancer_id,))
                    msg = 'Бүжигчин өмнөх бүртгэлтэй тул идэвхгүй болголоо'
                else:
                    cur.execute('DELETE FROM dancers WHERE id = ?', (dancer_id,))
                    msg = 'Бүжигчин бүрэн устгагдлаа'
                conn.commit()
                self.send_json({'success': True, 'message': msg})

            elif path.startswith('/api/records/'):
                record_id = int(path.split('/')[-1])
                cur.execute('DELETE FROM daily_records WHERE id = ?', (record_id,))
                conn.commit()
                self.send_json({'success': True, 'message': 'Бүртгэл устгагдлаа'})

            else:
                self.send_error(404, "API endpoint not found")
        finally:
            conn.close()

    # ================= EXCEL EXPORT =================
    def handle_export_excel(self, params):
        conn = get_db()
        cur = conn.cursor()

        club_id = params.get('club_id', [None])[0]
        start_date = params.get('start_date', [None])[0]
        end_date = params.get('end_date', [None])[0]

        query = '''
            SELECT d.stage_name, d.real_name, d.bank_account, d.dancer_type,
                   c.name as club_name,
                   COUNT(r.id) as shifts_count,
                   SUM(r.tip_qty) as total_tip_qty,
                   SUM(r.wine_reg_qty) as total_wine_reg_qty,
                   SUM(r.wine_exp_qty) as total_wine_exp_qty,
                   SUM(r.sit_reg_qty) as total_sit_reg_qty,
                   SUM(r.sit_drink_qty) as total_sit_drink_qty,
                   SUM(r.extra_qty) as total_extra_qty,
                   SUM(r.extra_amount) as total_extra,
                   SUM(r.penalty_amount) as total_penalty,
                   SUM(r.total_amount) as grand_total
            FROM daily_records r
            JOIN dancers d ON r.dancer_id = d.id
            JOIN clubs c ON r.club_id = c.id
            WHERE 1=1
        '''
        args = []
        if club_id and club_id != 'all':
            query += ' AND r.club_id = ?'
            args.append(club_id)
        if start_date and end_date:
            query += ' AND r.date BETWEEN ? AND ?'
            args.extend([start_date, end_date])

        query += ' GROUP BY d.id ORDER BY grand_total DESC'
        cur.execute(query, args)
        rows = cur.fetchall()
        conn.close()

        # Create Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Бүжигчдийн Бонус Тайлан"

        header_fill = PatternFill(start_color="181F2C", end_color="181F2C", fill_type="solid")
        header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=13, bold=True, color="111827")
        border = Border(
            left=Side(style='thin', color='E5E7EB'),
            right=Side(style='thin', color='E5E7EB'),
            top=Side(style='thin', color='E5E7EB'),
            bottom=Side(style='thin', color='E5E7EB')
        )

        date_str = f"{start_date} - {end_date}" if start_date and end_date else "Бүх хугацаа"
        ws['A1'] = f"БҮЖИГЧДИЙН ОРЛОГО, БОНУСЫН НЭГДСЭН ТАЙЛАН ({date_str})"
        ws['A1'].font = title_font
        ws.row_dimensions[1].height = 25

        headers = [
            "№", "Салбар", "Бүжигчний нэр", "Овог нэр", "Дансны дугаар",
            "Төрөл", "Ээлж", "TIP", "Энгийн Wine", "Үнэтэй Wine",
            "Энгийн суулт", "Уулттай суулт", "Extra (тоо)", "Extra (дүн)", "Торгууль", "НИЙТ ОЛГОХ БОНУС"
        ]

        for col_num, h in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_num)
            cell.value = h
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.row_dimensions[3].height = 24

        row_idx = 4
        for idx, r in enumerate(rows, 1):
            ws.cell(row=row_idx, column=1, value=idx).alignment = Alignment(horizontal="center")
            ws.cell(row=row_idx, column=2, value=r['club_name'])
            ws.cell(row=row_idx, column=3, value=r['stage_name']).font = Font(bold=True)
            ws.cell(row=row_idx, column=4, value=r['real_name'] or '-')
            ws.cell(row=row_idx, column=5, value=r['bank_account'] or '-').number_format = '@'
            ws.cell(row=row_idx, column=6, value=r['dancer_type'])
            ws.cell(row=row_idx, column=7, value=r['shifts_count']).alignment = Alignment(horizontal="right")
            ws.cell(row=row_idx, column=8, value=r['total_tip_qty'] or 0).alignment = Alignment(horizontal="right")
            ws.cell(row=row_idx, column=9, value=r['total_wine_reg_qty'] or 0).alignment = Alignment(horizontal="right")
            ws.cell(row=row_idx, column=10, value=r['total_wine_exp_qty'] or 0).alignment = Alignment(horizontal="right")
            ws.cell(row=row_idx, column=11, value=r['total_sit_reg_qty'] or 0).alignment = Alignment(horizontal="right")
            ws.cell(row=row_idx, column=12, value=r['total_sit_drink_qty'] or 0).alignment = Alignment(horizontal="right")
            ws.cell(row=row_idx, column=13, value=r['total_extra_qty'] or 0).alignment = Alignment(horizontal="right")
            ws.cell(row=row_idx, column=14, value=r['total_extra'] or 0).number_format = '#,##0₮'
            ws.cell(row=row_idx, column=15, value=r['total_penalty'] or 0).number_format = '#,##0₮'
            
            tot_cell = ws.cell(row=row_idx, column=16, value=r['grand_total'] or 0)
            tot_cell.font = Font(bold=True, color="047857")
            tot_cell.number_format = '#,##0₮'

            for c in range(1, 17):
                ws.cell(row=row_idx, column=c).border = border
            row_idx += 1

        # Summary Row
        ws.cell(row=row_idx, column=3, value="НИЙТ ДҮН:").font = Font(bold=True)
        sum_cell = ws.cell(row=row_idx, column=16, value=f"=SUM(P4:P{row_idx-1})")
        sum_cell.font = Font(bold=True, size=11, color="B91C1C")
        sum_cell.number_format = '#,##0₮'

        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        file_bytes = output.read()

        self.send_response(200)
        self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.send_header('Content-Disposition', f'attachment; filename="Dancers_Bonus_Report_{datetime.date.today().strftime("%Y%m%d")}.xlsx"')
        self.send_header('Content-Length', str(len(file_bytes)))
        self.end_headers()
        self.wfile.write(file_bytes)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), BarAppHandler) as httpd:
        print(f"Bar Dance Bonus App running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == '__main__':
    run()

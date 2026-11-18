import sqlite3
import openpyxl
import os

DB_PATH = 'bar_system.db'

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clubs table
    cur.execute('''
    CREATE TABLE clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')

    # Tariffs table
    cur.execute('''
    CREATE TABLE tariffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_id INTEGER NOT NULL,
        dancer_type TEXT NOT NULL, -- 'Үндсэн' or 'Халтуур'
        item_key TEXT NOT NULL,    -- 'tip', 'wine_reg', 'wine_exp', 'sit_reg', 'sit_drink', 'extra'
        item_name TEXT NOT NULL,
        rate INTEGER NOT NULL,
        FOREIGN KEY (club_id) REFERENCES clubs (id)
    )
    ''')

    # Dancers table
    cur.execute('''
    CREATE TABLE dancers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_id INTEGER NOT NULL,
        stage_name TEXT NOT NULL,
        real_name TEXT,
        bank_account TEXT,
        phone TEXT,
        dancer_type TEXT DEFAULT 'Үндсэн',
        tag TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (club_id) REFERENCES clubs (id)
    )
    ''')

    # Daily Records table (Bartender entries)
    cur.execute('''
    CREATE TABLE daily_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        club_id INTEGER NOT NULL,
        dancer_id INTEGER NOT NULL,
        tip_qty INTEGER DEFAULT 0,
        tip_amount INTEGER DEFAULT 0,
        wine_reg_qty INTEGER DEFAULT 0,
        wine_reg_amount INTEGER DEFAULT 0,
        wine_exp_qty INTEGER DEFAULT 0,
        wine_exp_amount INTEGER DEFAULT 0,
        sit_reg_qty INTEGER DEFAULT 0,
        sit_reg_amount INTEGER DEFAULT 0,
        sit_drink_qty INTEGER DEFAULT 0,
        sit_drink_amount INTEGER DEFAULT 0,
        extra_qty INTEGER DEFAULT 0,
        extra_amount INTEGER DEFAULT 0,
        penalty_amount INTEGER DEFAULT 0,
        total_amount INTEGER DEFAULT 0,
        bartender_name TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (club_id) REFERENCES clubs (id),
        FOREIGN KEY (dancer_id) REFERENCES dancers (id)
    )
    ''')

    # 1. Initial 3 Clubs
    clubs_data = [
        ('ARUM CLUB', 'ARUM', 'Салбар 1 - Arum Club'),
        ('ALOHA CLUB', 'ALOHA', 'Салбар 2 - Aloha Club'),
        ('MAN CLUB', 'MAN', 'Салбар 3 - Man Club')
    ]
    cur.executemany('INSERT INTO clubs (name, code, description) VALUES (?, ?, ?)', clubs_data)
    conn.commit()

    cur.execute('SELECT id, code FROM clubs')
    club_map = {code: cid for cid, code in cur.fetchall()}

    # 2. Tariffs - Official 11/18 Service Price List across all branches
    tariffs_data = []
    for code in ['ARUM', 'ALOHA', 'MAN']:
        cid = club_map[code]
        sit_drink_name = 'TABLE SIT MAN' if code == 'MAN' else 'DRINKABLE TABLE SERVICE'
        # Үндсэн бүжигчид (Main Dancers)
        tariffs_data.extend([
            (cid, 'Үндсэн', 'tip', 'TIP (Тип)', 15000),
            (cid, 'Үндсэн', 'wine_reg', 'WINE /энгийн/', 110000),
            (cid, 'Үндсэн', 'wine_exp', 'WINE /үнэтэй/', 180000),
            (cid, 'Үндсэн', 'sit_reg', 'TABLE SERVICE (Энгийн)', 70000),
            (cid, 'Үндсэн', 'sit_drink', sit_drink_name, 130000),
            (cid, 'Үндсэн', 'extra', 'Extra бонус', 200000),
            (cid, 'Үндсэн', 'taxi', 'TAXI TAX (Такси татвар)', 40000),
            # Халтуур (Freelance)
            (cid, 'Халтуур', 'tip', 'TIP (Тип)', 15000),
            (cid, 'Халтуур', 'wine_reg', 'WINE /энгийн/', 90000),
            (cid, 'Халтуур', 'wine_exp', 'WINE /үнэтэй/', 130000),
            (cid, 'Халтуур', 'sit_reg', 'TABLE SERVICE (Энгийн)', 50000),
            (cid, 'Халтуур', 'sit_drink', sit_drink_name, 110000),
            (cid, 'Халтуур', 'extra', 'Extra бонус', 200000),
            (cid, 'Халтуур', 'taxi', 'TAXI TAX (Такси татвар)', 40000),
        ])

    cur.executemany('''
    INSERT INTO tariffs (club_id, dancer_type, item_key, item_name, rate)
    VALUES (?, ?, ?, ?, ?)
    ''', tariffs_data)
    conn.commit()

    # 3. Import all dancers from Excel as 'Үндсэн'
    wb = openpyxl.load_workbook('Үндсэн бүжигчид_11_17.xlsx', data_only=True)
    sheet = wb['Бүжигчид']
    current_club = 'ARUM'

    dancer_rows = []

    for r in range(1, sheet.max_row + 1):
        c1 = sheet.cell(r, 1).value
        c2 = sheet.cell(r, 2).value
        c3 = sheet.cell(r, 3).value
        c4 = sheet.cell(r, 4).value
        c5 = sheet.cell(r, 5).value

        s1 = str(c1 or '').strip().upper()
        if 'ARUM CLUB' in s1:
            current_club = 'ARUM'
            continue
        elif 'ALOHA CLUB' in s1:
            current_club = 'ALOHA'
            continue
        elif 'MAN 444' in s1 or 'MAN CLUB' in s1:
            current_club = 'MAN'
            continue

        if c3 in ['Халтуур', 'Бүжигчний нэр', None]:
            continue
        if c4 in ['Данс эзэмшигчийн нэр', 'Өөрийн нэр']:
            continue

        stage_name = str(c3).strip()
        bank_owner = str(c4).strip() if c4 else ''
        bank_acc = str(c5).strip() if c5 else ''
        tag = str(c2).strip() if c2 else ''

        if stage_name:
            cid = club_map[current_club]
            # Normalize bank account and name for deduplication
            clean_acc = str(bank_acc).strip().upper().replace(' ', '')
            clean_owner = str(bank_owner).strip().lower()
            dedup_key = (clean_acc, clean_owner) if clean_acc and clean_owner else (stage_name.lower(), cid)
            
            if 'seen_dancer_keys' not in locals():
                seen_dancer_keys = set()
            
            if dedup_key not in seen_dancer_keys:
                seen_dancer_keys.add(dedup_key)
                dancer_rows.append((cid, stage_name, bank_owner, bank_acc, 'Үндсэн', tag))

    cur.executemany('''
    INSERT INTO dancers (club_id, stage_name, real_name, bank_account, dancer_type, tag)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', dancer_rows)
    conn.commit()

    # 4. Insert sample records from handwritten paper (2026-11-14, ARUM Club)
    # 1: Дөк        TIP: 12, Wine Reg: 1, table: 2 (regular), Total: 420,000
    # 2: Содука     TIP: 5, Wine Reg: 1, table: 0, Total: 175,000
    # 3: Ижилт      TIP: 14, Wine Reg: 1, table: 1 (regular), Total: 380,000
    # 4: Дүүрий     TIP: 4, table: 1 (drink), Extra: 80,000, Total: 260,000
    # 5: Хуланжин   TIP: 3, Wine Reg: 1, table: 1 (regular), Total: 215,000
    # 6: Чука       TIP: 13, Wine Reg: 1, table: 2 (regular), Total: 435,000
    # 7: Чулуун     TIP: 5, table: 2 (regular), Total: 215,000
    # 8: Айтиш      TIP: 10, table: 3 (regular), Total: 510,000
    # 9: Гоо (100)  TIP: 8, Wine Reg: 1, table: 1 (regular) + 40,000, Total: 330,000
    sample_handwritten = [
        ('Дөк', 'Зориг Нандин-Эрдэнэ', '320005005312841138', 12, 1, 0, 2, 0, 0, 0, 0, 420000),
        ('Содука', 'Дэлгэрзаяа', '900005005250242017', 5, 1, 0, 0, 0, 0, 0, 0, 175000),
        ('Ижилт', 'Цэндмаа', '850005005249438365', 14, 1, 0, 1, 0, 0, 0, 0, 380000),
        ('Дүүрий', 'Солонго', '260039008001073005', 4, 0, 0, 0, 1, 0, 80000, 0, 260000),
        ('Хуланжин', 'Хулан', '930005005159051390', 3, 1, 0, 1, 0, 0, 0, 0, 215000),
        ('Чука', 'Мөнхшүр', '820005005020870917', 13, 1, 0, 2, 0, 0, 0, 0, 435000),
        ('Чулуун', 'Нандин-Эрдэнэ', '240004004004264869', 5, 0, 0, 2, 0, 0, 0, 0, 215000),
        ('Айтиш', 'Алтансоёмбо', '480005005619124655', 10, 0, 0, 3, 0, 0, 0, 0, 510000),
        ('Гоо (100)', 'Нарансолонго', '360034270101858031', 8, 1, 0, 1, 0, 0, 40000, 0, 330000),
    ]

    arum_id = club_map['ARUM']
    for s_name, r_name, acc, tip, w_reg, w_exp, s_reg, s_drk, ex_qty, extra, pen, tot in sample_handwritten:
        cur.execute("SELECT id FROM dancers WHERE club_id=? AND stage_name=?", (arum_id, s_name))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO dancers (club_id, stage_name, real_name, bank_account, dancer_type) VALUES (?, ?, ?, ?, 'Үндсэн')",
                        (arum_id, s_name, r_name, acc))
            d_id = cur.lastrowid
        else:
            d_id = row[0]

        cur.execute('''
        INSERT INTO daily_records (
            date, club_id, dancer_id, tip_qty, tip_amount,
            wine_reg_qty, wine_reg_amount, wine_exp_qty, wine_exp_amount,
            sit_reg_qty, sit_reg_amount, sit_drink_qty, sit_drink_amount,
            extra_qty, extra_amount, penalty_amount, total_amount, bartender_name, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '2026-11-14', arum_id, d_id,
            tip, tip * 15000,
            w_reg, w_reg * 100000,
            w_exp, w_exp * 120000,
            s_reg, s_reg * 70000,
            s_drk, s_drk * 120000,
            ex_qty, extra, pen, tot,
            'Б.Заяа (Жишээ)', 'Цаасан тайлангаас шивсэн жишээ'
        ))

    conn.commit()
    conn.close()
    print("Database initialization complete with Wine categories & Extra tariff!")

if __name__ == '__main__':
    init_db()

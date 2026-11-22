-- ========================================================
-- BOUDOIR & NIGHT APP - SUPABASE REAL-TIME DATABASE SCHEMA
-- ========================================================

-- 1. DROP EXISTING TABLES IF ANY
DROP TABLE IF EXISTS records CASCADE;
DROP TABLE IF EXISTS taxi_pr_records CASCADE;
DROP TABLE IF EXISTS staff_tips CASCADE;
DROP TABLE IF EXISTS submitted_shifts CASCADE;
DROP TABLE IF EXISTS dancers CASCADE;
DROP TABLE IF EXISTS tariffs CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS clubs CASCADE;

-- 2. CREATE TABLES
CREATE TABLE clubs (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    address TEXT,
    color TEXT,
    taxi_rate NUMERIC DEFAULT 15000
);
CREATE TABLE dancers (
    id BIGINT PRIMARY KEY,
    stage_name TEXT NOT NULL,
    real_name TEXT,
    bank_account TEXT,
    club_id BIGINT,
    clubs JSONB,
    dancer_type TEXT DEFAULT 'Үндсэн',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE tariffs (
    id BIGINT PRIMARY KEY,
    club_id BIGINT,
    dancer_type TEXT,
    service_key TEXT,
    service_name TEXT,
    rate NUMERIC DEFAULT 0
);
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    club_id TEXT,
    club_code TEXT,
    is_blocked INTEGER DEFAULT 0
);
CREATE TABLE records (
    id BIGINT PRIMARY KEY,
    date TEXT NOT NULL,
    club_id BIGINT NOT NULL,
    club_name TEXT,
    club_code TEXT,
    dancer_id BIGINT NOT NULL,
    stage_name TEXT,
    real_name TEXT,
    bank_account TEXT,
    dancer_type TEXT,
    tip_qty INTEGER DEFAULT 0,
    wine_reg_qty INTEGER DEFAULT 0,
    wine_exp_qty INTEGER DEFAULT 0,
    sit_reg_qty INTEGER DEFAULT 0,
    sit_drink_qty INTEGER DEFAULT 0,
    extra_qty INTEGER DEFAULT 0,
    extra_amount NUMERIC DEFAULT 0,
    penalty_amount NUMERIC DEFAULT 0,
    total_amount NUMERIC DEFAULT 0,
    bartender_name TEXT,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE taxi_pr_records (
    id BIGINT PRIMARY KEY,
    type TEXT NOT NULL,
    date TEXT NOT NULL,
    club_id BIGINT NOT NULL,
    club_name TEXT,
    bartender_name TEXT,
    driver_name TEXT,
    driver_bank TEXT,
    taxi_qty INTEGER DEFAULT 0,
    rate NUMERIC DEFAULT 0,
    pr_manager_name TEXT,
    pr_manager_bank TEXT,
    bill_no TEXT,
    amount NUMERIC DEFAULT 0,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE staff_tips (
    id BIGINT PRIMARY KEY,
    club_id BIGINT NOT NULL,
    club_name TEXT,
    date TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    role TEXT,
    bank_account TEXT,
    amount NUMERIC DEFAULT 0,
    note TEXT,
    bartender_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE submitted_shifts (
    id TEXT PRIMARY KEY,
    club_id BIGINT NOT NULL,
    date TEXT NOT NULL,
    submitted_at TEXT,
    bartender_name TEXT,
    total_dancers INTEGER DEFAULT 0,
    grand_total NUMERIC DEFAULT 0,
    status TEXT DEFAULT 'submitted',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. DISABLE ROW LEVEL SECURITY (FULL ACCESS FOR APP CLIENTS)
ALTER TABLE clubs DISABLE ROW LEVEL SECURITY;
ALTER TABLE dancers DISABLE ROW LEVEL SECURITY;
ALTER TABLE tariffs DISABLE ROW LEVEL SECURITY;
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE records DISABLE ROW LEVEL SECURITY;
ALTER TABLE taxi_pr_records DISABLE ROW LEVEL SECURITY;
ALTER TABLE staff_tips DISABLE ROW LEVEL SECURITY;
ALTER TABLE submitted_shifts DISABLE ROW LEVEL SECURITY;

-- 4. ENABLE REALTIME BROADCASTING FOR ALL TABLES
ALTER PUBLICATION supabase_realtime ADD TABLE records, taxi_pr_records, staff_tips, submitted_shifts, dancers, tariffs, users, clubs;

-- 5. INSERT INITIAL SEED DATA
INSERT INTO clubs (id, name, code, address, color, taxi_rate) VALUES (1, 'ARUM CLUB', 'ARUM', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO clubs (id, name, code, address, color, taxi_rate) VALUES (2, 'ALOHA CLUB', 'ALOHA', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO clubs (id, name, code, address, color, taxi_rate) VALUES (3, 'MAN CLUB', 'MAN', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (70, 'Айтиш', 'Алтансоёмбо', '480005005619124655', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (10, 'Анжи', 'Анхжаргал', '480005005619124655', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (7, 'Гоо', 'Нарансолонго', '360034270101858031', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (67, 'Дүүрий', 'Солонго', '260039008001073005', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (1, 'Дөк', 'Зориг Нандин-Эрдэнэ', '320005005312841138', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (66, 'Ижилт', 'Цэндмаа', '850005005249438365', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (8, 'Лили', 'Анардалай', '830015001605316099', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (5, 'Намуунаа', 'Дэмбэрэлцэрэн Хишигт', '600005005562134223', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (11, 'Саруул', 'Баатархуяг Азжаргал', '190015001205301376', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (65, 'Содука', 'Дэлгэрзаяа', '900005005250242017', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (9, 'Содуна', 'Азжаргал', '900005005250242017', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (12, 'Хуланжин', 'Отгонцэцэг хулан', 'MN930005005159051390', 1, '[1, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (2, 'Хүслэн', 'Намхайдорж Цэндмаа', '850005005249438365', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (68, 'Чука', 'Мөнхшүр', '820005005020870917', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (69, 'Чулуун', 'Нандин-Эрдэнэ', '240004004004264869', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (15, 'Шүүдэрээ', 'Мөнхнасан', '430005005517499494', 1, '[1, 2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (14, 'Эгшиг', 'Сэлэнгэ', '460005005011773256', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (4, 'Энэрэл', 'Бат-Орших Солонго', '260039008001073005', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (3, 'Үжин', 'Болдбаатар Мөнхшүр', '820005005020870917', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (6, 'Үнзила', 'Лхагваа Ганболор', '600004004005732122', 1, '[1]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (28, 'Angel', 'Анужин Адьяа', '120004000471060358', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (23, 'NOX', '', '980005005422657336', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (31, 'Анасия', 'Үүрцайх', '920004000499516584', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (18, 'Аялгуу', 'Идэрхүү Нямхишиг', '410005005223092211', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (27, 'Бадмаараг', 'Сайнбилэг', '700015001175152858', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (33, 'Балу', 'Ундрах', '210005005622312270', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (22, 'Гоо', 'Анар', 'MN750050099106967162', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (35, 'Есү', 'Мандуул', '190050099106151624', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (32, 'Минжин', 'Минжин', '800005005058955287', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (25, 'Мишээл', 'Ариунзул', '210015003455185300', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (19, 'Нами', 'Ариунжаргал', '350004004005734415', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (26, 'Нова', 'Намуунзул', '040015002205303746', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (16, 'Роза', 'Ролзодмаа', 'MN260005005466209304', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (17, 'Сарнай', 'Жамбалдож Мягмарбаяр', '260005005901290291', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (30, 'Сийлэн', 'Хулан Ууганбаяр', '340034150001863392', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (34, 'Төрөө', 'Батмандах', '620032005005609402', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (29, 'Хүслэнт', 'Баясгалан Ганболд', '350015001605194452', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (20, 'Цэгц', 'Маралчимид', '040015001805304361', 2, '[2, 3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (21, 'Цэлмэг', 'Сарангоо', '400004004004116656', 2, '[2]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (50, 'Araba', 'Мөнххүслэн', '530005005375030758', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (60, 'Gaaraa', 'Амгаланбаатар', '740005005286357345', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (64, 'Geak', 'Жамба', '130005005618122693', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (56, 'Kevin', 'Эрдэнэбат Баясаа', '950005005423042092', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (57, 'Lotus', 'Сайнбилэг', '710005005624458853', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (63, 'NOXI', 'Батбаяр', '980005005422657336', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (55, 'Баяраа', '', '', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (61, 'Бэк', 'Очирбилгүүн', '730005005302240434', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (62, 'Бямбаа', '', '830005005404578261', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (49, 'Бөртэ', 'энхтүвшин  лхамсэржим', 'MN670058880005223339', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (59, 'Жамба', '', '', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (54, 'Тамираа', 'Анхбаяр', '910005005310200900', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (53, 'Төрөө', 'Гандорж Батмандах', '620032005005609402', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (36, 'Хүслэнт', 'Баясгалан', '350015001605194452', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO dancers (id, stage_name, real_name, bank_account, club_id, clubs, dancer_type) VALUES (43, 'Үүрээ', 'Бат-Эрдэнэ Эрдэнэбат', '100005005197470510', 3, '[3]'::jsonb, 'Үндсэн') ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (1, 1, 'Үндсэн', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (2, 1, 'Үндсэн', NULL, NULL, 110000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (3, 1, 'Үндсэн', NULL, NULL, 180000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (4, 1, 'Үндсэн', NULL, NULL, 70000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (5, 1, 'Үндсэн', NULL, NULL, 130000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (6, 1, 'Үндсэн', NULL, NULL, 200000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (7, 1, 'Үндсэн', NULL, NULL, 40000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (8, 1, 'Халтуур', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (9, 1, 'Халтуур', NULL, NULL, 90000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (10, 1, 'Халтуур', NULL, NULL, 130000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (11, 1, 'Халтуур', NULL, NULL, 50000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (12, 1, 'Халтуур', NULL, NULL, 110000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (13, 1, 'Халтуур', NULL, NULL, 200000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (14, 1, 'Халтуур', NULL, NULL, 40000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (15, 2, 'Үндсэн', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (16, 2, 'Үндсэн', NULL, NULL, 110000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (17, 2, 'Үндсэн', NULL, NULL, 180000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (18, 2, 'Үндсэн', NULL, NULL, 70000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (19, 2, 'Үндсэн', NULL, NULL, 130000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (20, 2, 'Үндсэн', NULL, NULL, 200000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (21, 2, 'Үндсэн', NULL, NULL, 40000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (22, 2, 'Халтуур', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (23, 2, 'Халтуур', NULL, NULL, 90000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (24, 2, 'Халтуур', NULL, NULL, 130000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (25, 2, 'Халтуур', NULL, NULL, 50000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (26, 2, 'Халтуур', NULL, NULL, 110000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (27, 2, 'Халтуур', NULL, NULL, 200000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (28, 2, 'Халтуур', NULL, NULL, 40000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (29, 3, 'Үндсэн', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (30, 3, 'Үндсэн', NULL, NULL, 110000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (31, 3, 'Үндсэн', NULL, NULL, 180000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (32, 3, 'Үндсэн', NULL, NULL, 70000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (33, 3, 'Үндсэн', NULL, NULL, 130000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (34, 3, 'Үндсэн', NULL, NULL, 200000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (35, 3, 'Үндсэн', NULL, NULL, 40000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (36, 3, 'Халтуур', NULL, NULL, 15000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (37, 3, 'Халтуур', NULL, NULL, 90000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (38, 3, 'Халтуур', NULL, NULL, 130000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (39, 3, 'Халтуур', NULL, NULL, 50000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (40, 3, 'Халтуур', NULL, NULL, 110000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (41, 3, 'Халтуур', NULL, NULL, 200000) ON CONFLICT (id) DO NOTHING;
INSERT INTO tariffs (id, club_id, dancer_type, service_key, service_name, rate) VALUES (42, 3, 'Халтуур', NULL, NULL, 40000) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (1, 'admin', '123', 'Ерөнхий нягтлан', 'admin', 'all', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (2, 'arum_bar1', '123', 'Арум Бармен 1', 'bartender', '1', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (3, 'arum_bar2', '123', 'Арум Бармен 2', 'bartender', '1', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (4, 'arum_mgr', '123', 'Арум Менежер', 'manager', '1', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (5, 'aloha_bar1', '123', 'Алоха Бармен 1', 'bartender', '2', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (6, 'aloha_bar2', '123', 'Алоха Бармен 2', 'bartender', '2', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (7, 'aloha_mgr', '123', 'Алоха Менежер', 'manager', '2', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (8, 'man_bar1', '123', 'Ман Бармен 1', 'bartender', '3', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (9, 'man_bar2', '123', 'Ман Бармен 2', 'bartender', '3', NULL, 0) ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, username, password, name, role, club_id, club_code, is_blocked) VALUES (10, 'man_mgr', '123', 'Ман Менежер', 'manager', '3', NULL, 0) ON CONFLICT (id) DO NOTHING;
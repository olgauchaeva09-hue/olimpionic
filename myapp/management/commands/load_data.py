import csv
import io
from django.core.management.base import BaseCommand
from myapp.models import Subject, Topic, Card, Olympiad, University

class Command(BaseCommand):
    help = 'Загрузка данных из Excel (скопированных в CSV)'

    def handle(self, *args, **options):
        # ===== ЛИСТ 1: ВУЗЫ =====
        universities_csv = """ВУЗ/олимпиада,ссылка
Казанский (Приволжский) федеральный университет,https://admissions.kpfu.ru/wp-content/uploads/2026/01/prilozhenie_3_pp2026_1-ot-27.01-poslednyaya.pdf
МГИМО,https://abiturient.mgimo.ru/bakalavriat/lgoty
МГТУ им. Н.Э. Баумана,https://kf.bmstu.ru/bakalavriat-i-specialitet/olimpiady
МГУ имени М.В. Ломоносова,https://cpk.msu.ru/files/2026/olymp_benefits.pdf
МИРЭА — Российский технологический университет,https://priem.mirea.ru/first-degree/entering/olymp
Московский государственный лингвистический университет,https://linguanet.ru/pk/pobeditelyam_i_prizeram_olimpiad.php
Московский физико-технический институт,https://pk.mipt.ru/bachelor/2026_olympiads/
НИУ ВШЭ,https://ba.hse.ru/bolimp
НИУ «МЭИ»,https://pk.mpei.ru/info/Oprava
Новосибирский государственный университет,https://www.nsu.ru/n/education/apply-info/olimpiady-privilege/
Первый МГМУ им. И.М. Сеченова,https://www.sechenov.ru/upload/iblock/8e9/6494g8cw4lewtgoy79j18dl2zll3yxyz/BS-Prilozhenie-_3-k-Pravilam-priema-2025_2026.pdf
РАНХиГС,https://www.ranepa.ru/bakalavriat/olimpiady/
РГГУ,https://www.rsuh.ru/upload/main/priem25/bac/2025_БАК_СПЕЦ_Особые_права_для_победителей_и_призеров_олимпиад.pdf
РГУ им. А. Н. Косыгина,https://rguk.ru/applicant/admission-rules/bakalavriat/special-rules/
РНИМУ им. Н.И. Пирогова,https://priem.mai.ru/orders/contest-winners/
РУДН,https://priem.rudn.ru/olympiady
РЭУ им. Г.В. Плеханова,https://www.rea.ru/~file/133487/Pravila_priema_2025_bak_pril14.pdf
Санкт-Петербургский горный университет,https://priem.spmi.ru/olimpiady
СПбГУ,https://abiturient.spbu.ru/medialibrary/ru/2023/bac/bac_spec_olymp_2.pdf
СПбПУ Петра Великого,https://www.spbstu.ru/abit/bachelor/oznakomitsya-with-the-regulations/olympics/
Университет Иннополис,https://apply.innopolis.university/olympiad-bonus/
ИТМО,https://abit.itmo.ru/bachelor
МИСИС,https://misis.ru/applicants/admission/baccalaureate-and-specialty/olympiad/school/
УрФУ,https://izumrud.urfu.ru/ru/about/benefits/
Финансовый университет,https://www.fa.ru/for-applicants/olympiads/uchet/"""

        reader = csv.DictReader(io.StringIO(universities_csv))
        for row in reader:
            name = row['ВУЗ/олимпиада'].strip()
            link = row['ссылка'].strip()
            uni, created = University.objects.get_or_create(
                university_name=name,
                defaults={'link': link}
            )
            if created:
                self.stdout.write(f'[Университет] {name}')

        # ===== ЛИСТ 2: ПРЕДМЕТЫ, ТЕМЫ, КАРТОЧКИ =====
        materials_csv = """предмет,тема,ссылка,тип материала,название,олимпиада
право,общее,https://www.consultant.ru/,сайт,Справочная правовая система КонсультантПлюс,любая
право,международное право,https://www.un.org/ru/,сайт,Сайт ООН для изучения международного права,любая
право,общее,https://postnauka.org/,сайт,ПостНаука — материалы по праву,любая
право,теория права,,книга,Ростовцева Н. В. Теория государства и права,любая
право,история права,,книга,Владимирский-Буданов М. Ф. Обзор истории русского права,любая
право,гражданское право,,книга,Покровский И. А. Основные проблемы гражданского права,любая
право,семейное право,,книга,Пчелинцева Л. М. Практикум по семейному праву,любая
право,уголовное право,https://postnauka.org/faq/69584,статья,Суд присяжных,любая
право,социология права,https://postnauka.org/courses/47305,курс,Социология права (ПостНаука),любая
право,история права,https://postnauka.org/video/62477,видео,Закон в постсоветский период,любая
право,история права,https://postnauka.org/longreads/50386,статья,Великая хартия вольностей,любая
право,международное право,http://www.aup.ru/books/m232/,книга,В.Т. Батычко Международное право,любая
право,международное право,https://elar.urfu.ru/bitstream/10995/42381/1/978-5-7996-1805-6_2016.pdf,книга,Меньшенина Н.Н. Международное право (учебное пособие),любая
право,уголовное право,https://samara.mgpu.ru/files/library_elektron/YUrisp/Ugol_pravo.pdf,книга,Галактионов С.А. Уголовное право (курс лекций),любая
право,семейное право,https://elsu.ru/uploads/files/2023-01/1674313163_lavrischeva-o_a_-semejnoe-pravo.pdf,книга,Лаврищева О.А. Семейное право (учебное пособие),любая
право,семейное право,https://www.consultant.ru/document/cons_doc_LAW_8982/,кодекс,Семейный кодекс РФ,любая
право,,http://olymp.hse.ru/mmo/materials-law,демоверсии,Демоверсии Высшая проба право,Высшая проба
право,,http://olymp.hse.ru/mmo/tasks-law,варианты,Задания прошлых лет Высшая проба право,Высшая проба
право,,https://mos.olimpiada.ru/olymp/law,варианты,Задания прошлых лет МОШ право,Московская олимпиада школьников
право,,https://rutube.ru/video/d45762177f9633a50268552c0dbd3c45/,видео,Разбор региона ВСОШ право 9 класс,Всероссийская олимпиада школьников
право,,https://rutube.ru/video/c6fa7a99e6af4ff67126af5ab8489d0b/,видео,Разбор региона ВСОШ право 10 класс,Всероссийская олимпиада школьников
право,,https://rutube.ru/video/7998b9d85b8828ef8bf2c02f92b608d6/,видео,Разбор региона ВСОШ право 11 класс,Всероссийская олимпиада школьников
право,римское право,https://postnauka.org/courses/17335,курс,Римское право (ПостНаука),любая
экономика,общее,https://solvehub.app/econ/problems/list/70336,задачи,База задач по экономике,любая
экономика,общее,https://solvehub.app/econ/tests/training,тесты,Тесты по экономике,любая
экономика,основы микроэкономики,https://solvehub.app/econ/lib/article/41,статья,Адам Смит,любая
экономика,общее,https://www.rulit.me/books/ekonomist-na-divane,книга,Экономист на диване,любая
экономика,макроэкономика,http://elib.rshu.ru/files_books/pdf/rid_048e04056c7b4a60a35e5d663b3ece8c.pdf,книга,Гагулина Н.Л. Макроэкономика,любая
экономика,общее,https://postnauka.org/guides/156703,курс,О криптовалюте фондовом рынке и коррупции,любая
экономика,мировая экономика,https://postnauka.org/video/75752,видео,Международная торговля,любая
экономика,макроэкономика,https://postnauka.org/video/36242,видео,Фискальная и монетарная политика,любая
экономика,мировая экономика,http://elib.rshu.ru/files_books/pdf/rid_d731a2278264475a8ebddcba290cff8b.pdf,книга,Островская Е.Н. Мировая экономика,любая
экономика,,https://olymp.hse.ru/mmo/tasks-eco,варианты,Задания прошлых лет Высшая проба экономика,Высшая проба
экономика,,https://olymp.hse.ru/mmo/materials-eco,демоверсии,Демоверсии Высшая проба экономика,Высшая проба
экономика,,https://olimpiada.ru/activity/110/tasks,варианты,Задания прошлых лет МОШ экономика,Московская олимпиада школьников
экономика,,https://olimpiada.ru/activity/5172/tasks,варианты,Задания прошлых лет Плехановская олимпиада,Плехановская олимпиада
экономика,основы микроэкономики,,книга,Вэриан Х.Р. Микроэкономика (промежуточный уровень),любая"""

        olympiads_cache = {}
        subjects_cache = {}
        topics_cache = {}

        reader = csv.DictReader(io.StringIO(materials_csv))
        for row in reader:
            subject_name = row['предмет'].strip()
            topic_name = row['тема'].strip()
            link = row['ссылка'].strip()
            material_type = row['тип материала'].strip()
            title = row['название'].strip()
            olympiad_name = row['олимпиада'].strip()

            if not subject_name or not title:
                continue

            # Предмет
            if subject_name not in subjects_cache:
                subj, _ = Subject.objects.get_or_create(
                    subject_name=subject_name,
                    defaults={'icon': '📚'}
                )
                subjects_cache[subject_name] = subj
            subject = subjects_cache[subject_name]

            # Тема (может быть пустой)
            topic = None
            if topic_name:
                topic_key = f"{subject_name}:{topic_name}"
                if topic_key not in topics_cache:
                    top, _ = Topic.objects.get_or_create(
                        topic_name=topic_name,
                        subject=subject
                    )
                    topics_cache[topic_key] = top
                topic = topics_cache[topic_key]

            # Олимпиада
            olympiad = None
            if olympiad_name and olympiad_name != 'любая':
                if olympiad_name not in olympiads_cache:
                    oly, _ = Olympiad.objects.get_or_create(olympiad_name=olympiad_name)
                    olympiads_cache[olympiad_name] = oly
                olympiad = olympiads_cache[olympiad_name]

            # Тип материала → type_number
            type_map = {
                'книга': 0, 'учебник': 0, 'словарь': 0, 'кодекс': 0, 'журнал': 0,
                'статья': 1, 'видео': 2, 'курс': 2, 'подкаст': 2,
                'задачи': 3, 'тесты': 3, 'варианты': 3, 'демоверсии': 3,
                'сайт': 4, 'атласы': 4, 'коллекция': 4,
            }
            type_number = type_map.get(material_type, 0)

            # Создаём карточку
            card = Card.objects.create(
                title=title,
                type_number=type_number,
                type=material_type,
                xp=10,
                link=link if link else None,
                source=olympiad_name if olympiad_name != 'любая' else None
            )
            if topic:
                card.topic.add(topic)

            self.stdout.write(f'[Карточка] {title[:60]}')

        self.stdout.write(self.style.SUCCESS('ГОТОВО: данные загружены'))
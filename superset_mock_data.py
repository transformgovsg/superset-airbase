import random
import logging
import time
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from psycopg2.extras import execute_batch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/tmp/script.log"), logging.StreamHandler()],
)

# Start timing
start_time = time.time()
logging.info("Starting mock data generation script")

# Constants
STUDENTS_PER_CLASS = 5
CLASS_SUFFIXES = ["A", "B", "C", "D", "E", "F", "G", "H"]
LEVELS = [
    ("SEC1", "Secondary 1"),
    ("SEC2", "Secondary 2"),
    ("SEC3", "Secondary 3"),
    ("SEC4", "Secondary 4"),
]
SCHOOLS = {
    "SC001": "ADMIRALTY SECONDARY SCHOOL",
    "SC002": "AHMAD IBRAHIM SECONDARY SCHOOL",
    "SC003": "ANDERSON SECONDARY SCHOOL",
    "SC004": "ANG MO KIO SECONDARY SCHOOL",
    "SC005": "ANGLICAN HIGH SCHOOL",
    "SC006": "ANGLO-CHINESE SCHOOL (BARKER ROAD)",
    "SC007": "ANGLO-CHINESE SCHOOL (INDEPENDENT)",
    "SC008": "ASSUMPTION ENGLISH SCHOOL",
    "SC009": "BARTLEY SECONDARY SCHOOL",
    "SC010": "BEATTY SECONDARY SCHOOL",
    "SC011": "BEDOK GREEN SECONDARY SCHOOL",
    "SC012": "BEDOK SOUTH SECONDARY SCHOOL",
    "SC013": "BEDOK VIEW SECONDARY SCHOOL",
    "SC014": "BENDEMEER SECONDARY SCHOOL",
    "SC015": "BOON LAY SECONDARY SCHOOL",
    "SC016": "BOWEN SECONDARY SCHOOL",
    "SC017": "BROADRICK SECONDARY SCHOOL",
    "SC018": "BUKIT BATOK SECONDARY SCHOOL",
    "SC019": "BUKIT MERAH SECONDARY SCHOOL",
    "SC020": "BUKIT PANJANG GOVT. HIGH SCHOOL",
    "SC021": "BUKIT VIEW SECONDARY SCHOOL",
    "SC022": "CANBERRA SECONDARY SCHOOL",
    "SC023": "CATHOLIC HIGH SCHOOL",
    "SC024": "CEDAR GIRLS' SECONDARY SCHOOL",
    "SC025": "CHANGKAT CHANGI SECONDARY SCHOOL",
    "SC026": "CHIJ KATONG CONVENT",
    "SC027": "CHIJ SECONDARY (TOA PAYOH)",
    "SC028": "CHIJ ST. JOSEPH'S CONVENT",
    "SC029": "CHIJ ST. NICHOLAS GIRLS' SCHOOL",
    "SC030": "CHIJ ST. THERESA'S CONVENT",
    "SC031": "CHRIST CHURCH SECONDARY SCHOOL",
    "SC032": "CHUA CHU KANG SECONDARY SCHOOL",
    "SC033": "CHUNG CHENG HIGH SCHOOL (MAIN)",
    "SC034": "CHUNG CHENG HIGH SCHOOL (YISHUN)",
    "SC035": "CLEMENTI TOWN SECONDARY SCHOOL",
    "SC036": "COMMONWEALTH SECONDARY SCHOOL",
    "SC037": "COMPASSVALE SECONDARY SCHOOL",
    "SC038": "CRESCENT GIRLS' SCHOOL",
    "SC039": "DAMAI SECONDARY SCHOOL",
    "SC040": "DEYI SECONDARY SCHOOL",
    "SC041": "DUNEARN SECONDARY SCHOOL",
    "SC042": "DUNMAN HIGH SCHOOL",
    "SC043": "DUNMAN SECONDARY SCHOOL",
    "SC044": "EAST SPRING SECONDARY SCHOOL",
    "SC045": "EDGEFIELD SECONDARY SCHOOL",
    "SC046": "EVERGREEN SECONDARY SCHOOL",
    "SC047": "FAIRFIELD METHODIST SCHOOL (SECONDARY)",
    "SC048": "FAJAR SECONDARY SCHOOL",
    "SC049": "FUCHUN SECONDARY SCHOOL",
    "SC050": "FUHUA SECONDARY SCHOOL",
    "SC051": "GAN ENG SENG SCHOOL",
    "SC052": "GEYLANG METHODIST SCHOOL (SECONDARY)",
    "SC053": "GREENDALE SECONDARY SCHOOL",
    "SC054": "GREENRIDGE SECONDARY SCHOOL",
    "SC055": "GUANGYANG SECONDARY SCHOOL",
    "SC056": "HAI SING CATHOLIC SCHOOL",
    "SC057": "HILLGROVE SECONDARY SCHOOL",
    "SC058": "HOLY INNOCENTS' HIGH SCHOOL",
    "SC059": "HOUGANG SECONDARY SCHOOL",
    "SC060": "HUA YI SECONDARY SCHOOL",
    "SC061": "HWA CHONG INSTITUTION",
    "SC062": "JUNYUAN SECONDARY SCHOOL",
    "SC063": "JURONG SECONDARY SCHOOL",
    "SC064": "JURONG WEST SECONDARY SCHOOL",
    "SC065": "JURONGVILLE SECONDARY SCHOOL",
    "SC066": "JUYING SECONDARY SCHOOL",
    "SC067": "KENT RIDGE SECONDARY SCHOOL",
    "SC068": "KRANJI SECONDARY SCHOOL",
    "SC069": "KUO CHUAN PRESBYTERIAN SECONDARY SCHOOL",
    "SC070": "LOYANG VIEW SECONDARY SCHOOL",
    "SC071": "MANJUSRI SECONDARY SCHOOL",
    "SC072": "MARIS STELLA HIGH SCHOOL",
    "SC073": "MARSILING SECONDARY SCHOOL",
    "SC074": "MAYFLOWER SECONDARY SCHOOL",
    "SC075": "MERIDIAN SECONDARY SCHOOL",
    "SC076": "METHODIST GIRLS' SCHOOL (SECONDARY)",
    "SC077": "MONTFORT SECONDARY SCHOOL",
    "SC078": "NAN CHIAU HIGH SCHOOL",
    "SC079": "NAN HUA HIGH SCHOOL",
    "SC080": "NANYANG GIRLS' HIGH SCHOOL",
    "SC081": "NATIONAL JUNIOR COLLEGE",
    "SC082": "NAVAL BASE SECONDARY SCHOOL",
    "SC083": "NEW TOWN SECONDARY SCHOOL",
    "SC084": "NGEE ANN SECONDARY SCHOOL",
    "SC085": "NORTH VISTA SECONDARY SCHOOL",
    "SC086": "NORTHBROOKS SECONDARY SCHOOL",
    "SC087": "NORTHLAND SECONDARY SCHOOL",
    "SC088": "ORCHID PARK SECONDARY SCHOOL",
    "SC089": "OUTRAM SECONDARY SCHOOL",
    "SC090": "PASIR RIS CREST SECONDARY SCHOOL",
    "SC091": "PASIR RIS SECONDARY SCHOOL",
    "SC092": "PAYA LEBAR METHODIST GIRLS' SCHOOL (SEC)",
    "SC093": "PEI HWA SECONDARY SCHOOL",
    "SC094": "PEICAI SECONDARY SCHOOL",
    "SC095": "PEIRCE SECONDARY SCHOOL",
    "SC096": "PING YI SECONDARY SCHOOL",
    "SC097": "PRESBYTERIAN HIGH SCHOOL",
    "SC098": "PUNGGOL SECONDARY SCHOOL",
    "SC099": "QUEENSTOWN SECONDARY SCHOOL",
    "SC100": "QUEENSWAY SECONDARY SCHOOL",
    "SC101": "RAFFLES GIRLS' SCHOOL (SECONDARY)",
    "SC102": "RAFFLES INSTITUTION",
    "SC103": "REGENT SECONDARY SCHOOL",
    "SC104": "RIVER VALLEY HIGH SCHOOL",
    "SC105": "RIVERSIDE SECONDARY SCHOOL",
    "SC106": "SEMBAWANG SECONDARY SCHOOL",
    "SC107": "SENG KANG SECONDARY SCHOOL",
    "SC108": "SERANGOON GARDEN SECONDARY SCHOOL",
    "SC109": "SERANGOON SECONDARY SCHOOL",
    "SC110": "SINGAPORE CHINESE GIRLS' SCHOOL",
    "SC111": "SPRINGFIELD SECONDARY SCHOOL",
    "SC112": "ST. ANDREW'S SECONDARY SCHOOL",
    "SC113": "ST. ANTHONY'S CANOSSIAN SECONDARY SCHOOL",
    "SC114": "ST. GABRIEL'S SECONDARY SCHOOL",
    "SC115": "ST. HILDA'S SECONDARY SCHOOL",
    "SC116": "ST. JOSEPH'S INSTITUTION",
    "SC117": "ST. MARGARET'S SECONDARY SCHOOL",
    "SC118": "ST. PATRICK'S SCHOOL",
    "SC119": "SWISS COTTAGE SECONDARY SCHOOL",
    "SC120": "TAMPINES SECONDARY SCHOOL",
    "SC121": "TANGLIN SECONDARY SCHOOL",
    "SC122": "TANJONG KATONG GIRLS' SCHOOL",
    "SC123": "TANJONG KATONG SECONDARY SCHOOL",
    "SC124": "TECK WHYE SECONDARY SCHOOL",
    "SC125": "TEMASEK JUNIOR COLLEGE",
    "SC126": "TEMASEK SECONDARY SCHOOL",
    "SC127": "UNITY SECONDARY SCHOOL",
    "SC128": "VICTORIA SCHOOL",
    "SC129": "WEST SPRING SECONDARY SCHOOL",
    "SC130": "WESTWOOD SECONDARY SCHOOL",
    "SC131": "WHITLEY SECONDARY SCHOOL",
    "SC132": "WOODGROVE SECONDARY SCHOOL",
    "SC133": "WOODLANDS RING SECONDARY SCHOOL",
    "SC134": "WOODLANDS SECONDARY SCHOOL",
    "SC135": "XINMIN SECONDARY SCHOOL",
    "SC136": "YIO CHU KANG SECONDARY SCHOOL",
    "SC137": "YISHUN SECONDARY SCHOOL",
    "SC138": "YISHUN TOWN SECONDARY SCHOOL",
    "SC139": "YUAN CHING SECONDARY SCHOOL",
    "SC140": "YUHUA SECONDARY SCHOOL",
    "SC141": "YUYING SECONDARY SCHOOL",
    "SC142": "ZHENGHUA SECONDARY SCHOOL",
    "SC143": "ZHONGHUA SECONDARY SCHOOL",
}
SURNAMES = [
    "Tan",
    "Lim",
    "Lee",
    "Li",
    "Ng",
    "Wong",
    "Wang",
    "Chan",
    "Chen",
    "Ong",
    "Goh",
    "Chua",
    "Chai",
    "Teo",
    "bin Abdullah",
    "bin Ahmad",
    "bin Mohamed",
    "bin Muhammad",
    "bin Ibrahim",
    "Kumar",
    "Singh",
    "Raj",
    "Syed",
    "Pillai",
    "Krishnan",
    "Ramasamy",
    "Govindasamy",
    "Shankar",
    "Sharma",
]
NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Emma",
    "Fiona",
    "George",
    "Henry",
    "Ian",
    "Jane",
    "Kelly",
    "Linda",
    "Mary",
    "Nancy",
    "Oliver",
    "Peter",
    "Quinn",
    "Rachel",
    "Sarah",
    "Tom",
    "Uma",
    "Victor",
    "Wendy",
    "Xavier",
    "Yolanda",
    "Zack",
    "Wei Ming",
    "Jun Jie",
    "Wei Jian",
    "Zhong Wei",
    "Jun Hong",
    "Wei Liang",
    "Kah Chun",
    "Ming Yi",
    "Chee Hian",
    "Yong Sheng",
    "Wei Xiang",
    "Zhi Hao",
    "Xiang Long",
    "Jia Jun",
    "Ming Xuan",
    "Hui Ling",
    "Xin Yi",
    "Mei Ying",
    "Shu Hui",
    "Li Ting",
    "Hui Min",
    "Jia Xin",
    "Wei Ting",
    "Hui Wen",
    "Mei Ling",
    "Xin Yi",
    "Jia Ying",
    "Hui En",
    "Shu Ping",
    "Hui Ying",
    "Wei",
    "Way",
    "Jun",
    "Juin",
    "Ming",
    "Hong",
    "Jie",
    "Jiet",
    "Hui",
    "Mei",
    "Ying",
    "Xin",
    "Ling",
]

COMPETENCIES = [
    {"intent_id": "1", "name": "Competency 1"},
    {"intent_id": "1", "name": "Competency 2"},
    {"intent_id": "1", "name": "Competency 3"},
    {"intent_id": "1", "name": "Competency 4"},
    {"intent_id": "2", "name": "Competency 5"},
    {"intent_id": "2", "name": "Competency 6"},
    {"intent_id": "2", "name": "Competency 7"},
    {"intent_id": "2", "name": "Competency 8"},
    {"intent_id": "3", "name": "Competency 9"},
    {"intent_id": "3", "name": "Competency 10"},
]

QUESTIONS_LOWER = [
    {
        "id": 1,
        "text": "Question 1 for Lower Secondary level",
        "competency": "Competency 1",
        "intent_id": "1",
    },
]

QUESTIONS_UPPER = [
    {
        "id": 1,
        "text": "Question 1 for Upper Secondary level",
        "competency": "Competency 1",
        "intent_id": "1",
    },
]

RESPONSES = {
    1: "Response 1",
    2: "Response 2",
    3: "Response 3",
    4: "Response 4",
}

level_to_year = {
    "SEC1": 2021,
    "SEC2": 2022,
    "SEC3": 2023,
    "SEC4": 2024,
}

DB_PARAMS = {
    "host": "/tmp",
    "database": "superset",
    "user": "superset",
    "password": "superset",
    "port": 5432,
}

BATCH_SIZE = 50000


def generate_responses_batch():
    batch = []
    sg_tz = ZoneInfo("Asia/Singapore")
    timestamps = [
        datetime(2024, 1, 1, tzinfo=sg_tz),
        datetime(2024, 7, 1, tzinfo=sg_tz),
    ]
    for school_code, school_name in SCHOOLS.items():
        for class_suffix in CLASS_SUFFIXES:
            for i in range(1, STUDENTS_PER_CLASS + 1):
                student_name = f"{random.choice(NAMES)} {random.choice(SURNAMES)}"
                for level_code, level_name in LEVELS:
                    class_code = f"{level_code[-1]}{class_suffix}"
                    class_name = f"Class {class_code}"
                    student_id = f"{school_code}_{level_code}_{class_code}_{i:03d}"
                    academic_year = level_to_year[level_code]
                    student_info = {
                        "school_code": school_code,
                        "school_name": school_name,
                        "level_code": level_code,
                        "level_name": level_name,
                        "class_code": class_code,
                        "class_name": class_name,
                        "student_id": student_id,
                        "student_name": student_name,
                    }
                    question_set = (
                        QUESTIONS_LOWER
                        if level_code in ["SEC1", "SEC2"]
                        else QUESTIONS_UPPER
                    )
                    for published_at in timestamps:
                        for q in question_set:
                            response_value = random.randint(1, 4)
                            response_text = RESPONSES[response_value]
                            batch.append(
                                (
                                    student_info["school_code"],
                                    student_info["school_name"],
                                    student_info["level_code"],
                                    student_info["level_name"],
                                    student_info["class_code"],
                                    student_info["class_name"],
                                    student_info["student_id"],
                                    student_info["student_name"],
                                    academic_year,
                                    q["id"],
                                    q["text"],
                                    q["competency"],
                                    q["intent_id"],
                                    response_value,
                                    response_text,
                                    published_at,
                                )
                            )
                            if len(batch) >= BATCH_SIZE:
                                yield batch
                                batch = []
    if batch:
        yield batch


def insert_batch_to_postgres(batch, conn):
    insert_query = """
    INSERT INTO student_responses (
        school_code, school_name, level_code, level_name, 
        class_code, class_name, student_id, student_name,
        academic_year, question_id, question_text, competency,
        intent_id, response_value, response_text, published_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cursor:
        execute_batch(cursor, insert_query, batch, page_size=1000)
    conn.commit()


def main():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        logging.info("Successfully connected to database")

        # Test connection
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            logging.info("Database connection test successful")

        total_inserted = 0
        for batch_num, batch in enumerate(generate_responses_batch(), 1):
            logging.info(f"Inserting batch {batch_num} with {len(batch)} records...")
            insert_batch_to_postgres(batch, conn)
            total_inserted += len(batch)
            logging.info(f"Total inserted so far: {total_inserted}")
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
    finally:
        if "conn" in locals():
            conn.close()
        logging.info("Database connection closed")
        elapsed = time.time() - start_time
        logging.info(
            f"Script completed. Total records inserted: {total_inserted} in {elapsed:.2f} seconds"
        )


if __name__ == "__main__":
    main()

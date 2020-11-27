import mysql.connector
import os

# Connects to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="sr",
    auth_plugin="mysql_native_password"
)

cursor = db.cursor()


def drop_tables():
    """Drops tables if they exist"""
    cursor.execute('''
        DROP TABLE IF EXISTS sr.nurses;
    ''')

    db.commit()


def create_nurse_table():
    """Creates the nurse table if it doesn't exist"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sr.nurses
        (id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(250) NOT NULL,
        clinical_area VARCHAR(250),
        foo VARCHAR(15),
        rotation VARCHAR(250),
        group_num INT,
        fte DECIMAL(3,2),
        skill_level INT,
        a_trained TINYINT(1),
        transfer TINYINT(1),
        iv TINYINT(1),
        advanced_role VARCHAR(250),
        previous_patients VARCHAR(250),
        dta VARCHAR(250),
        comments VARCHAR(250),
        priority TINYINT(1),
        current_shift VARCHAR(250),
        PRIMARY KEY (id));'''
                   )
    db.commit()


def create_patient_table():
    """Creates the patient table if it doesn't exist"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sr.patients
        (id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(250) NOT NULL,
        clinical_area VARCHAR(100),
        bed_num INT,
        acuity INT,
        a_trained TINYINT(1),
        transfer TINYINT(1),
        iv TINYINT(1),
        one_to_one TINYINT(1),
        previous_nurses VARCHAR(250),
        admission_date VARCHAR(250),
        discharged_date VARCHAR(250),
        comments VARCHAR(250),
        twin VARCHAR(250),
        PRIMARY KEY (id));'''
                   )
    db.commit()


def open_file(file):
    """Reads the contents of the CSV file into a list"""
    nurse_file = open(os.path.abspath(file))
    nurse_old_list = nurse_file.readlines()

    # Removes last row in CSV
    nurse_old_list.pop(-1)

    return nurse_old_list


def strip_new_lines(nurse_old_list):
    """Strips the \n from the list items"""
    nurse_new_list = []

    for row in nurse_old_list:
        row = row.strip("\n")
        nurse_new_list.append(row)

    return nurse_new_list


def split_list(nurse_new_list):
    """Creates nurse lists adds them to big list"""
    nurse_big_list = []

    for column in nurse_new_list:
        column = column.split(",")

        # Gets rid of the empty rows in CSV
        if column[0] != '':
            nurse_big_list.append(column)

    if nurse_big_list[0][0] == 'Casuals':
        num = 0
    else:
        group, num = nurse_big_list[0][0].split(' ')

    return nurse_big_list, num


def insert_into_nurse_table(nurse_list):
    """Inserts the nurse data from CSV into the database"""
    for nurse in nurse_list:

        cursor.execute(
            'INSERT INTO nurses (name, clinical_area, foo, '
            'rotation, group_num, fte, skill_level, a_trained, transfer, '
            'iv, advanced_role, previous_patients, dta, comments, priority, '
            'current_shift) '
            'VALUES '
            '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (nurse[0], nurse[1], nurse[2], nurse[3],
             nurse[4], str(nurse[5]), nurse[7], nurse[6],
             nurse[8], nurse[12], nurse[9], nurse[10],
             nurse[11], nurse[15], nurse[13], nurse[14]
             )
        )

    db.commit()


def get_nurse_formatted_list(file):
    """Returns the CSV list and group number"""
    nurse_data_list = open_file(file)
    nurse_stripped_list = strip_new_lines(nurse_data_list)
    nurse_formatted_list, group_num = split_list(nurse_stripped_list)
    nurse_formatted_list.pop(0)

    return nurse_formatted_list, group_num


def insert_new_columns_for_nurse(nurse):
    """Inserts the missing columns from database"""
    nurse.insert(2, None)
    nurse.insert(4, '')
    nurse.insert(11, '')
    nurse.insert(12, '')
    nurse.insert(14, '')
    nurse.insert(15, '')
    nurse.pop(10)


def validate_columns(nurse, group_num):
    """Fixes values in spreadsheet to match database schema"""

    if nurse[count] == 'Yes' or nurse[count] == 'yes':
        set_to_one(nurse)

    if nurse[count] == 'L' and nurse.index(nurse[count]) == 12:
        nurse[count] = 3

    if nurse[count] == '':
        fix_empty_values(nurse, group_num)

    if nurse[count] == 'Casual':
        nurse[count] = 0

    if nurse.index(nurse[count]) == 15:
        nurse[count] += ', ' + str(nurse[16])

    if nurse.index(nurse[count]) == 16:
        nurse.pop(16)


def fix_empty_values(nurse, group_num):
    """Performs validation on empty cells"""
    if nurse.index(nurse[count]) == 4:
        nurse[count] = group_num

    elif nurse.index(nurse[count]) == 8 or nurse.index(nurse[count]) == 6 \
            or nurse.index(nurse[count]) == 13 or nurse.index(nurse[count]) == 14 \
            or nurse.index(nurse[count]) == 5:
        nurse[count] = 0

    elif nurse.index(nurse[count]) == 12:
        nurse[count] = 1

    elif nurse.index(nurse[count]) == 10:
        nurse[count] = '[]'

    else:
        nurse[count] = None


def set_to_one(nurse):
    """Sets IV column to 1 or 2"""
    if nurse.index(nurse[count]) == 12:
        nurse[count] = 2
    else:
        nurse[count] = 1


if __name__ == '__main__':
    print('Importing Data...\n')

    drop_tables()
    create_nurse_table()
    create_patient_table()

    for file in os.listdir(os.getcwd()):

        if file.endswith('csv'):
            nurse_formatted_list, group_num = get_nurse_formatted_list(file)

            for nurse in nurse_formatted_list:
                insert_new_columns_for_nurse(nurse)

                for count in range(0, len(nurse)):
                    validate_columns(nurse, group_num)

            insert_into_nurse_table(nurse_formatted_list)

    print('Data has been successfully imported.')
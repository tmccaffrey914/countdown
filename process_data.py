import mysql.connector
from play import countdown_shuffle

DEFAULT_BATCH_SIZE = 999
WORDS_DB = mysql.connector.connect(
    host="localhost",
    user="root"
)


def get_total_number_of_words():
    cursor = WORDS_DB.cursor()
    cursor.execute("USE wn_pro_mysql;")
    cursor.execute("SELECT COUNT(*) FROM wn_synset")
    result = cursor.fetchone()
    cursor.close()
    return result[0]


def batcher(big_list, batch_size=1):
    """
    Split a list into batches. Useful for batch processing.
    :param big_list: A list with many elements
    :param batch_size: The max size of a batch in the new list
    :return: A list of lists, each sublist is of size `batch_size`
    """
    length = len(big_list)
    for index in range(0, length, batch_size):
        yield big_list[index:min(index + batch_size, length)]


def save_shuffled_word(cursor, shuffled_records, batch_size=DEFAULT_BATCH_SIZE):
    """
    Insert Shuffled versions of our Plaintext words into another Table
    """
    for batch in batcher(shuffled_records, batch_size):
        cursor.executemany("""
            INSERT IGNORE INTO shuffled_words
            VALUES (%s, %s, %s, %s, %s, %s);
        """, batch)
        print("Adding to Shuffle Table")
        WORDS_DB.commit()


def update_plaintext_table_with_sanitized_words(cursor, sanitized_map, batch_size=DEFAULT_BATCH_SIZE):
    """
    Update our Plain Text DB with any Corrections we have made during the "Shuffle and Insert" to the Second Table
    """
    for batch in batcher(sanitized_map, batch_size):
        cursor.executemany("""
            UPDATE wn_synset
            SET word=%s WHERE word=%s;
        """, batch)
        print("Adding to Plain Text Table")
        WORDS_DB.commit()


def purge_db_of_irrelevant_data(cursor):
    """
    Delete Data that is irrelevant to our purpose
    """
    cursor.execute("DELETE FROM wn_synset WHERE LENGTH(word) > 9;")
    cursor.execute("DELETE FROM wn_synset WHERE word LIKE '%\_%';")
    cursor.execute("DELETE FROM wn_synset WHERE word LIKE '%.%';")
    cursor.execute(r"DELETE FROM wn_synset WHERE word LIKE '%\'%';")  # Use Raw String to Prevent SQL Syntax Errors
    cursor.execute("DELETE FROM wn_synset WHERE word LIKE '%-%';")
    cursor.execute("DELETE FROM wn_synset WHERE word LIKE '%/%';")
    cursor.execute("DELETE FROM wn_synset WHERE word REGEXP '[0-9]';")


def process_words():
    cursor = WORDS_DB.cursor()
    cursor.execute("USE wn_pro_mysql;")

    # Create a Table Identical to the Plaintext one, so we can use the IDs to map Plaintext to Scrambled:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shuffled_words (
        synset_id decimal(10,0) NOT NULL,
        w_num decimal(10,0) NOT NULL,
        word varchar(50),
        ss_type char(2),
        sense_number decimal(10,0) NOT NULL,
        tag_count decimal(10,0),
        PRIMARY KEY(synset_id, w_num, word)
    );
    """)

    purge_db_of_irrelevant_data(cursor)

    cursor.execute("SELECT * FROM wn_synset;")

    # This will contain Tuples with the Countdown Shuffled Value and the Expected Plain Text Value:
    shuffled_records = []

    # Any Words Requiring Sanitization in the Plain Text Table will be stored here:
    sanitized_map = []

    while True:
        result = cursor.fetchmany(DEFAULT_BATCH_SIZE)

        if not result:
            break

        for row in result:
            plaintext_word = row[2]

            # find() Will return a negative Integer if the character wasn't found:
            if plaintext_word.find('(') >= 0:
                print("Found a Plaintext Word containing Brackets")
                # We know (from looking at the data) that some valid words contain
                # brackets at the end, we will parse & remove these:
                plaintext_word = plaintext_word[:plaintext_word.find('(')]
                sanitized_map.append((plaintext_word, row[2]))

            shuffled_records.append((row[0], row[1], countdown_shuffle(plaintext_word), row[3], row[4], row[5]))

    save_shuffled_word(cursor, shuffled_records)
    update_plaintext_table_with_sanitized_words(cursor, sanitized_map)

    cursor.close()


if __name__ == '__main__':
    print("Start Data Processing")
    process_words()

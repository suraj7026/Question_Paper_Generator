import streamlit as st
import mysql.connector
from mysql.connector import Error
import random


class Question:
    def __init__(self, qid, question, importance, mark, difficulty, subject_name, topic, question_type):
        self.qid = qid
        self.question = question
        self.importance = importance
        self.mark = mark
        self.difficulty = difficulty
        self.subject_name = subject_name
        self.topic = topic
        self.question_type = question_type


# Connect to the MySQL database
try:
    conn = mysql.connector.connect(
        host='localhost',
        database='question_bank',
        user='root',
        password='@Suraj2308'
    )

    if conn.is_connected():
        print('Connected to MySQL database')

        cursor = conn.cursor()

        def fetch_questions_from_database(importance=None, mark=None, difficulty=None, subject_name=None, topic=None, question_type=None):
            query = "SELECT * FROM questions WHERE "
            conditions = []

            if importance:
                conditions.append(f"importance = '{importance}'")
            if topic:
                conditions.append(f"topic = '{topic}'")
            if difficulty:
                conditions.append(f"difficulty = '{difficulty}'")
            if subject_name:
                conditions.append(f"subject_name = '{subject_name}'")
            if mark:
                conditions.append(f"mark = '{mark}'")
            if question_type:
                conditions.append(f"question_type = '{question_type}'")

            query += " AND ".join(conditions)

            cursor.execute(query)
            result = cursor.fetchall()

            # Convert the result to a list of Question objects
            questions = [Question(*row) for row in result]

            return questions

        def select_random_questions_from_database(n, importance=None, mark=None, difficulty=None, subject_name=None, topic=None,question_type=None):
            questions = fetch_questions_from_database(
                importance, mark, difficulty, subject_name, topic,question_type)

            if not questions:
                return None  # No matching questions found

            # Ensure balanced distribution of question types (you can customize this based on your needs)
            # question_types = set(q.question_type for q in questions)
            # selected_question_type = random.choice(list(question_types))

            # Select n random questions of the chosen type
            eligible_questions = [
                q for q in questions]
            selected_questions = random.sample(
                eligible_questions, min(n, len(eligible_questions)))

            return selected_questions

        # Example usage:
        num_questions = 5  # Set the number of questions to generate
        selected_questions = select_random_questions_from_database(
            num_questions, subject_name="Physics",question_type='MCQ')
        if selected_questions:
            for i, question in enumerate(selected_questions, start=1):
                print(f"Question {i}: {question.question}")
        else:
            print("No matching questions found.")

except Error as e:
    print(f"Error: {e}")

finally:
    # Close the database connection when done
    if conn.is_connected():
        cursor.close()
        conn.close()
        print('Connection closed.')

import streamlit as st
import mysql.connector
from mysql.connector import Error

class Question:
    def __init__(self, question, importance, difficulty, subject_name, topic, question_type):
        self.question = question
        self.importance = importance
        self.difficulty = difficulty
        self.subject_name = subject_name
        self.topic = topic
        self.question_type = question_type

def add_question_to_database(cursor, question):
    query = "INSERT INTO questions (Question, Importance, Difficulty, Subject_name, Topic, Question_type) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (question.question, question.importance, question.difficulty, question.subject_name, question.topic, question.question_type)
    cursor.execute(query, values)

# Streamlit UI
st.title("Add Questions")

# Connect to the MySQL database
try:
    conn = mysql.connector.connect(
        host='localhost',
        database='question_bank',
        user='root',
        password='@Suraj2308'
    )

    if conn.is_connected():
        cursor = conn.cursor()

        # User input for generating questions
        subject_name = st.selectbox(
            "Select the subject", ["Mathematics", "Physics", "Chemistry", "Computer Science", "Biology"])
        difficulty = st.selectbox(
            "Select the difficulty level", ["Easy", "Medium", "Hard"], index=1)  # Default to "Medium"
        importance = st.selectbox(
            "Select the importance level", ["Low", "Medium", "High"], index=1)  # Default to "Medium"
        topic = st.text_input("Enter the topic:")
        if subject_name in ["Chemistry", "Physics"]:
            question_type = st.selectbox(
                "Select the question type",
                ["MCQ", "Short Answer 2M", "Short Answer 3M", "Case-based", "Long Answer"]
            )
        elif subject_name in ["Computer Science", "Biology"]:
            question_type = st.selectbox(
                "Select the question types",
                ["1M", "2M", "3M", "4M", "5M"]
            )
        elif subject_name == "Mathematics":
            question_type = st.selectbox(
                "Select the question types",
                ["MCQ", "Assertion-Reason", "Very Short Answer", "Short Answer", "Long Answer", "Case-based"]
            )
        else:
            st.warning("Invalid subject selected")
        question_text = st.text_input("Enter the question:")

        # Button to add the question to the database
        if st.button("Add Question"):
            new_question = Question(question_text, importance, difficulty, subject_name, topic, question_type)
            add_question_to_database(cursor, new_question)
            conn.commit()
            st.success("Question added successfully!")

except Error as e:
    st.error(f"Error: {e}")

finally:
    # Close the database connection when done
    if conn.is_connected():
        cursor.close()
        conn.close()

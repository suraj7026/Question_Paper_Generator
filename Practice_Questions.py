import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Streamlit UI
st.title("Practice Question Generator")

# Connect to the MySQL database
try:
    db_config = st.secrets["mysql"]
    conn = st.connection(type='mysql', host=db_config["host"], database=db_config["database"],
                         user=db_config["user"], password=db_config["password"])

    if conn.is_connected():
        cursor = conn.cursor()

        class Question:
            def __init__(self, question, importance, difficulty, subject_name, topic, question_type):
                self.question = question
                self.importance = importance
                self.difficulty = difficulty
                self.subject_name = subject_name
                self.topic = topic
                self.question_type = question_type

        def fetch_questions_from_database(importance=None, mark=None, difficulty=None, subject_name=None, topic=None,
                                          question_type=None):
            query = "SELECT * FROM questions WHERE "
            conditions = []

            if importance:
                conditions.append(f"importance = '{importance}'")
            if topic:
                conditions.append(f"topic = '{topic}'")
            if difficulty:
                difficulty_conditions = [f"difficulty = '{d}'" for d in difficulty]
                conditions.append("(" + " OR ".join(difficulty_conditions) + ")")
            if subject_name:
                conditions.append(f"subject_name = '{subject_name}'")
            if mark:
                conditions.append(f"mark = '{mark}'")
            if question_type:
                question_type_conditions = [f"question_type = '{qtype}'" for qtype in question_type]
                conditions.append("(" + " OR ".join(question_type_conditions) + ")")

            query += " AND ".join(conditions)

            cursor.execute(query)
            result = cursor.fetchall()

            # Convert the result to a list of Question objects
            questions = [Question(*row) for row in result]

            return questions

        def select_ordered_questions_from_database(n, importance=None, mark=None, difficulty=None, subject_name=None,
                                                   topic=None, question_type=None):
            questions = fetch_questions_from_database(
                importance, mark, difficulty, subject_name, topic, question_type)

            if not questions:
                return None  # No matching questions found

            # Sort questions by type (MCQ, One Marks, Descriptive)
            sorted_questions = sorted(questions, key=lambda q: q.question_type)

            # Check if n is greater than the total number of questions
            if n > len(sorted_questions):
                st.warning("Requested number of questions exceeds available questions. Adjusting to the maximum available.")
                n = len(sorted_questions)

            # Select n random questions
            selected_questions = random.sample(sorted_questions, n)

            return selected_questions

        def generate_pdf(questions):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica", 12)

            for i, question in enumerate(questions, start=1):
                c.drawString(10, 750 - i * 12, f" {i}: {question.question}")

            c.save()

            buffer.seek(0)
            return buffer

        # User input for generating questions
        num_questions = st.slider("Select the number of questions", 1, 40, 5)
        subject_name = st.selectbox(
            "Select the subject", ["Mathematics", "Physics", "Chemistry", "Computer Science", "Biology"])
        difficulty = st.multiselect(
            "Select the difficulty level", ["Easy", "Medium", "Hard"], default=["Easy", "Hard"])

        if subject_name in ["Chemistry", "Physics"]:
            question_types = st.multiselect(
                "Select the question types",
                ["MCQ", "Short Answer 2M", "Short Answer 3M", "Case-based", "Long Answer"],
                default=["MCQ", "Short Answer 2M", "Short Answer 3M"]
            )
        elif subject_name in ["Computer Science", "Biology"]:
            question_types = st.multiselect(
                "Select the question types",
                ["1M", "2M", "3M", "4M", "5M"],
                default=["1M", "2M", "3M"]
            )
        elif subject_name == "Mathematics":
            question_types = st.multiselect(
                "Select the question types",
                ["MCQ", "Assertion-Reason", "Very Short Answer", "Short Answer", "Long Answer", "Case-based"],
                default=["MCQ", "Assertion-Reason", "Very Short Answer"]
            )
        else:
            st.warning("Invalid subject selected")

        importance = st.selectbox("Select the importance", ["High", "Medium", "Low"], index=1)  # Default to "Medium"

        # Generate questions based on user input
        selected_questions = select_ordered_questions_from_database(
            num_questions, difficulty=difficulty, subject_name=subject_name, question_type=question_types,
            importance=importance)

        # Display the generated questions
        if selected_questions:
            st.subheader("Generated Questions:")
            for i, question in enumerate(selected_questions, start=1):
                st.write(f"Question {i}: {question.question}")

            # Download PDF button
            pdf_buffer = generate_pdf(selected_questions)
            st.download_button(
                label="Download Questions as PDF", data=pdf_buffer, file_name="generated_questions.pdf", key="pdf_button"
            )

        else:
            st.warning("No matching questions found.")

except Error as e:
    st.error(f"Error: {e}")

finally:
    # Close the database connection when done
    if conn.is_connected():
        cursor.close()
        conn.close()

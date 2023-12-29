import streamlit as st

class Question:
    def __init__(self, qid, question, importance, difficulty, subject_name, topic, question_type):
        self.qid = qid
        self.question = question
        self.importance = importance
        self.difficulty = difficulty
        self.subject_name = subject_name
        self.topic = topic
        self.question_type = question_type


def fetch_questions_from_database(importance=None, mark=None, difficulty=None, subject_name=None, topic=None, question_type=None):
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


def select_ordered_questions_from_database(n, importance=None, mark=None, difficulty=None, subject_name=None, topic=None, question_type=None):
    questions = fetch_questions_from_database(
        importance, mark, difficulty, subject_name, topic, question_type)

    if not questions:
        return None  # No matching questions found

    # Sort questions by type (MCQ, One Marks, Descriptive)
    sorted_questions = sorted(questions, key=lambda q: q.question_type)

    # Select n random questions
    selected_questions = random.sample(
        sorted_questions, min(n, len(sorted_questions)))

    return selected_questions


def generate_section_questions_mathematics():
    section_a_questions = generate_section_questions(18, ["MCQ"])
    section_b_questions = generate_section_questions(2, ["Assertion-Reason"])
    section_c_questions = generate_section_questions(5, ["Very Short Answer"])
    section_d_questions = generate_section_questions(6, ["Short Answer"])
    section_e_questions = generate_section_questions(4, ["Long Answer"])
    section_f_questions = generate_section_questions(3, ["Source-Based/Case-Based"])

    return section_a_questions + section_b_questions + section_c_questions + section_d_questions + section_e_questions + section_f_questions


def generate_section_questions_chemistry_physics():
    section_a_questions = generate_section_questions(16, ["MCQ"])
    section_b_questions = generate_section_questions(5, ["Short Answer"])
    section_c_questions = generate_section_questions(7, ["Short Answer"])
    section_d_questions = generate_section_questions(2, ["Case-Based"])
    section_e_questions = generate_section_questions(3, ["Long Answer"])

    return section_a_questions + section_b_questions + section_c_questions + section_d_questions + section_e_questions


def generate_section_questions_computer_science_biology():
    section_a_questions = generate_section_questions(16, ["1M"])
    section_b_questions = generate_section_questions(5, ["2M"])
    section_c_questions = generate_section_questions(7, ["3M"])
    section_d_questions = generate_section_questions(2, ["4M"])
    section_e_questions = generate_section_questions(3, ["5M"])

    return section_a_questions + section_b_questions + section_c_questions + section_d_questions + section_e_questions


def generate_section_questions(n, question_types):
    selected_questions = select_ordered_questions_from_database(
        n, difficulty=["Easy", "Medium", "Hard"], subject_name=subject_name, question_type=question_types, importance="Medium"
    )

    if selected_questions:
        return [(f" {i+1}", question) for i, question in enumerate(selected_questions)]
    else:
        return []


def generate_pdf(subject_name, questions):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 16)

    # Add subject heading
    heading = "Question Paper - " + subject_name
    c.drawCentredString(300, 800, heading)
    c.setFont("Helvetica", 12)

    # Iterate through questions and format them
    y_position = 750
    line_height = 12
    indentation = 20  # Adjust the indentation as needed

    for i, (question_type, question) in enumerate(questions, start=1):
        formatted_question = question_type + ": " + question.question

        # Split lines based on newline character
        lines = formatted_question.split('\n')

        for line in lines:
            c.drawString(indentation, y_position, line)
            y_position -= line_height  # Adjust for the next line

        # Add extra space between questions
        y_position -= line_height

    c.save()

    buffer.seek(0)
    return buffer


# Streamlit UI
st.title("Practice Question Paper Generator")

# Connect to the MySQL database
try:
    conn = st.connection(type='mysql', host=db_config["host"], database=db_config["database"],
                         user=db_config["user"], password=db_config["password"])

    if conn.is_connected():
        cursor = conn.cursor()

        # User input for generating questions
        subject_name = st.selectbox(
            "Select the subject", ["Mathematics", "Physics", "Chemistry", "Computer Science", "Biology"])
        difficulty = st.selectbox(
            "Select the difficulty level", ["Easy", "Medium", "Hard"], index=1)  # Default to "Medium"

        # Generate questions based on the specified pattern for each section
        if subject_name == "Mathematics":
            all_questions = generate_section_questions_mathematics()
        elif subject_name in ["Chemistry", "Physics"]:
            all_questions = generate_section_questions_chemistry_physics()
        elif subject_name in ["Computer Science","Biology"]:
            all_questions = generate_section_questions_computer_science_biology()
        else:
            st.warning("Invalid subject selected")

        # Display the generated questions
        if all_questions:
            st.subheader("Generated Questions:")

            for i, (question_type, question) in enumerate(all_questions, start=1):
                st.write(f"{question_type}: {question.question}")

            # Download PDF button
            pdf_buffer = generate_pdf(subject_name, all_questions)
            st.download_button(
                label="Download Questions as PDF", data=pdf_buffer, file_name="generated_questions.pdf",
                key="pdf_button"
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



import os
import random
import qianfan
import streamlit as st
from docx import Document

# Set environment variables
os.environ["QIANFAN_ACCESS_KEY"] = "ALTAKgDF4odotcMdxlDyQteugV"
os.environ["QIANFAN_SECRET_KEY"] = "4f6933316001493d9efd93c95f331af5"

# Create ChatCompletion instance
chat_comp = qianfan.ChatCompletion()

# Prompts for generating questions and grading answers
CHOICE_PROMPT = """
Please read the following content carefully:\n\n{content}\n\n

Please write the questions in English
You are a professional and serious examiner tasked with creating high-quality questions for an exam. Based on the knowledge points in the content above, generate a single-choice question. The question should focus on a key concept, fact, or idea from the content. Do not provide the answer, any explanation, or additional commentary. This is an exam, and the question should be clear and unbiased.

Question: ____________
A. ___________
B. ___________
C. ___________
D. ___________
Answer will be revealed after submission.

Generate Rules:
1. The question must be based on the knowledge points covered in the provided content. Extract relevant information from the content to form the question.
2. The four options (A, B, C, D) must be distinct, logically meaningful, and not redundant. Each option should present a reasonable alternative or variation based on the content. Only one option should be correct.
3. The question must be single-choice, meaning there is one and only one correct answer. The correct answer should be clear and unambiguous.
4. Do not provide the answer, hints, or any additional commentary in your response. The correct answer should not be hinted at in any way.
5. The output must strictly follow the question format with only the question and options. No further explanation or clarification should be added.
6. The four options must cover different aspects of the content, such as different characteristics, applications, or consequences. Avoid overly simplistic or irrelevant choices.
7. Avoid repetition or overlap between the options, ensuring that each one offers a distinct and meaningful alternative.
"""

BLANK_PROMPT = """
Please read the following content carefully:\n\n{content}\n\n

You are a professional and serious examiner tasked with creating high-quality questions for an exam. Based on the knowledge points in the content above, generate a fill-in-the-blank question. The question should focus on a key concept, fact, or idea from the content. The blank should represent a missing piece of crucial information that can be inferred directly from the content. Do not provide the answer, any explanation, or additional commentary. This is an exam, and the question should be clear and unbiased.

Fill-in-the-blank: ___________

Generate Rules:
1. The fill-in-the-blank question must focus on a specific key point from the content. The blank should represent a missing piece of crucial information that can be inferred from the provided content.
2. Do not provide the answer or any explanation in your response. The content should be chosen so the blank can be filled with a specific word or concept directly derived from the content.
3. The question must be clear, direct, and easy for a person familiar with the content to fill in. Avoid leaving a blank that could have multiple valid answers unless the content clearly supports one.
4. Ensure that the blank is the only missing part of the sentence. The remaining context should help the user deduce what belongs in the blank.
5. Make sure the question is clear and direct with no unnecessary complexity or ambiguity.
"""

SHORT_ANSWER_PROMPT = """
Please read the following content carefully:\n\n{content}\n\n

You are a professional and serious examiner tasked with creating high-quality questions for an exam. Based on the knowledge points in the content above, generate a short-answer question. The question should focus on a key concept, fact, or idea from the content. The question should prompt the user to provide a concise answer based on their understanding of the content. Do not provide the answer, any explanation, or additional commentary. This is an exam, and the question should be clear and unbiased.

Short-answer question: ___________

Generate Rules:
1. The short-answer question should test the user’s ability to recall and articulate key details from the content. The question should require a response that concisely captures important information from the content.
2. Do not provide the answer or any explanation in your response. The short-answer question should ask the user to provide a clear, precise answer.
3. The question should be specific, requiring the user to provide a precise and factual answer. Avoid overly broad or open-ended questions that don't have a clear answer.
4. The question should reflect direct understanding of the content. The user should be able to answer based on their comprehension of the material.
5. Ensure that the question is clear and direct, with no unnecessary complexity or ambiguity.
"""

GRADE_PROMPT = """
Question: {question}
User's answer: {user_answer}

Please evaluate whether the user's answer is correct or not. Provide a brief judgment:
- If the answer is correct, confirm the correctness and provide a concise explanation of why it is correct.
- If the answer is incorrect, point out the error and provide a detailed explanation of the correct answer. Be specific and clear about the mistake and explain the correct concept or fact.

Generate Rules:
1. Ensure that the grading feedback is concise but sufficiently detailed. The explanation should highlight why the user’s answer is correct or incorrect, and clarify any misunderstanding if necessary.
2. The feedback should be tailored to the specific question. If the user’s answer is correct, affirm that it is correct and give a brief justification based on the content.
3. If the answer is incorrect, clearly identify the mistake and offer a clear, accurate explanation of the correct answer. Avoid over-explaining; the goal is to be direct and to the point.
4. The grading feedback should be relevant to the question type. If it’s a multiple-choice question, explain why the chosen option is correct or not. If it’s a short-answer question, clarify the correct term or concept the user was expected to provide.
5. Make sure the feedback is clear, precise, and helpful. Do not include any irrelevant information, and avoid using unnecessary words or phrases.
"""

# Extract text from Word file
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Use Qianfan to generate questions
def generate_question(content):
    choice = CHOICE_PROMPT.format(content=content)
    blank = BLANK_PROMPT.format(content=content)
    short_answer = SHORT_ANSWER_PROMPT.format(content=content)

    # Generate random number to decide question type
    rand_value = random.random()

    if rand_value < 0.6:
        prompt = choice
    elif rand_value < 0.9:
        prompt = blank
    else:
        prompt = short_answer

    response = chat_comp.do(
        model="ERNIE-Speed-8K",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['body']['result']

# Auto-grade answers
def grade_answer(question, user_answer):
    prompt = GRADE_PROMPT.format(question=question, user_answer=user_answer)
    response = chat_comp.do(
        model="ERNIE-Speed-8K",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['body']['result']

# Streamlit user interface
st.header("LLM-Based Intelligent Question-Generation and Assessment System")

# Predefined relative path for the document
file_path = "knowledge dase - media theory.docx"

if os.path.exists(file_path):
    content = extract_text_from_docx(file_path)
    st.info("Knowledge base loaded successfully!")

    # Initialize or update the current question
    if 'question' not in st.session_state:
        st.session_state['question'] = generate_question(content)  # Generate the first question

    # Display the current question
    question = st.session_state['question']
    
    # Format and display the multiple-choice options
    if "A" in question and "B" in question and "C" in question and "D" in question:
        formatted_question = question.replace("A.", "\nA.").replace("B.", "\nB.").replace("C.", "\nC.").replace("D.", "\nD.")
        st.markdown(formatted_question)
    else:
        st.write(question)

    # User answer input box
    user_answer = st.text_input(f"Please enter your answer:", key="user_answer")

    # Submit answer and grade
    if st.button("Submit Answer"):
        if user_answer.strip():  # Check if the user entered an answer
            result = grade_answer(question, user_answer)
            st.write(f"Grading Result: {result}")
        else:
            st.warning("Please enter an answer before submitting!")

    # Next question button
    if st.button("Next Question"):
        st.session_state['question'] = generate_question(content)  # Generate the next question
        st.rerun()  # Force a refresh to display the new question
else:
    st.error(f"The file '{file_path}' was not found. Please ensure it is in the correct directory.")

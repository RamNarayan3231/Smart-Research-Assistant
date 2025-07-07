import streamlit as st
import requests
import os

# Configure backend URL
BACKEND_URL = "http://localhost:8000"  # Update if your backend runs elsewhere

# Set page config
st.set_page_config(
    page_title="Research Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stTextInput>div>div>input {
        padding: 0.5rem;
    }
    .question-box {
        background-color: #2c2c2c;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .answer-box {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .evaluation-box {
        background-color: #3a3a3a;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📚 Smart Research Assistant")
    st.markdown("Upload a research document and interact with it in two ways: ask questions or test your understanding.")

    # Initialize session state
    for key, value in {
        'doc_id': None,
        'document_uploaded': False,
        'challenge_questions': [],
        'user_answers': {},
        'evaluations': {},
        'summary': ""
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.header("1. Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])

    if uploaded_file is not None:
        if st.button("Upload and Process"):
            with st.spinner("Processing..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{BACKEND_URL}/upload/", files=files)

                    if response.status_code == 200:
                        data = response.json()
                        if "doc_id" in data:
                            st.session_state.doc_id = data["doc_id"]
                            st.session_state.document_uploaded = True
                            st.session_state.summary = data.get("summary", "")
                            st.success("File processed successfully!")

                            if st.session_state.summary:
                                st.subheader("Document Summary")
                                st.write(st.session_state.summary)
                        else:
                            st.error(f"Error processing file: {data.get('detail', 'No detail provided')}")
                    else:
                        st.error(f"Error processing file: {response.text}")
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

    if st.session_state.document_uploaded and st.session_state.doc_id:
        st.header("2. Choose Interaction Mode")
        tab1, tab2 = st.tabs(["Ask Anything", "Challenge Me"])

        # --------------- ASK ANYTHING ---------------
        with tab1:
            st.subheader("Ask Anything")
            question = st.text_input("Enter your question about the document:")

            if st.button("Get Answer", key="get_answer_button") and question:
                with st.spinner("Finding answer..."):
                    try:
                        payload = {"question": question}
                        # response = requests.post(
                        #     f"{BACKEND_URL}/ask/{st.session_state.doc_id}",
                        #     json=payload
                        # )
                        response = requests.post(
                            f"{BACKEND_URL}/ask/{st.session_state.doc_id}",
                            params={"question": question}   # replace json= with params=
                        )

                        if response.status_code == 200:
                            data = response.json()
                            st.subheader("Answer")
                            st.markdown(f"<div class='answer-box'>{data.get('answer', 'No answer returned.')}</div>", unsafe_allow_html=True)
                            st.subheader("Justification")
                            st.write(data.get('justification', 'No justification returned.'))
                        else:
                            st.error(f"Error getting answer: {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            elif st.button("If empty", key="warn_get_answer_button") and not question:
                st.warning("Please enter a question before clicking 'Get Answer'.")

        # --------------- CHALLENGE ME ---------------
        with tab2:
            st.subheader("Challenge Me")

            if st.button("Generate Questions"):
                with st.spinner("Generating challenge questions..."):
                    try:
                        response = requests.get(
                            f"{BACKEND_URL}/challenge/{st.session_state.doc_id}"
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.challenge_questions = data.get("questions", [])
                            st.session_state.user_answers = {}
                            st.session_state.evaluations = {}
                            st.success("Questions generated successfully!")
                        else:
                            st.error(f"Error generating questions: {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

            if st.session_state.challenge_questions:
                st.subheader("Questions")
                for i, question in enumerate(st.session_state.challenge_questions):
                    st.markdown(f"<div class='question-box'><b>Question {i+1}:</b> {question}</div>", unsafe_allow_html=True)
                    answer_key = f"answer_{i}"
                    user_answer = st.text_input(f"Your answer to question {i+1}:", key=answer_key)
                    st.session_state.user_answers[i] = user_answer

                    if st.button(f"Evaluate Answer {i+1}", key=f"eval_btn_{i}"):
                        if user_answer.strip():
                            with st.spinner("Evaluating your answer..."):
                                try:
                                    payload = {"answer": user_answer}
                                    response = requests.post(
                                        f"{BACKEND_URL}/evaluate/{st.session_state.doc_id}/{i}",
                                        json=payload
                                    )
                                    if response.status_code == 200:
                                        data = response.json()
                                        st.session_state.evaluations[i] = data
                                        st.success("Answer evaluated!")
                                    else:
                                        st.error(f"Error evaluating answer: {response.text}")
                                except Exception as e:
                                    st.error(f"An error occurred: {str(e)}")
                        else:
                            st.warning("Please enter an answer before evaluating.")

                    if i in st.session_state.evaluations:
                        eval_data = st.session_state.evaluations[i]
                        
                        question_text = eval_data.get("question", "N/A")
                        user_answer = eval_data.get("user_answer", "N/A")
                        evaluation_details = eval_data.get("evaluation", {})
                        score = evaluation_details.get("score", "N/A")
                        evaluation_text = evaluation_details.get("evaluation", "N/A")
                        ideal_answer = evaluation_details.get("ideal_answer", "N/A")

                        st.markdown(f"""
                        <div class='evaluation-box'>
                            <b>Evaluation:</b> {evaluation_text}<br><br>
                            
                        </div>
                        """, unsafe_allow_html=True)

                        '''
                        st.markdown(f"""
                        <div class='evaluation-box'>
                            <b>Question:</b> {question_text}<br><br>
                            <b>Your Answer:</b> {user_answer}<br><br>
                            <b>Score:</b> {score} / 5<br><br>
                            <b>Evaluation:</b> {evaluation_text}<br><br>
                            <b>Ideal Answer:</b> {ideal_answer}
                        </div>
                        """, unsafe_allow_html=True) '''



if __name__ == "__main__":
    main()


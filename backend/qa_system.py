from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from backend.openrouter_llm import OpenRouterLLM
from typing import List, Tuple, Dict
import re
import io

class QASystem:
    def __init__(self):
        self.llm = OpenRouterLLM()
        
        # Improved prompt templates
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            As a research assistant, carefully analyze the context and provide:
            1. A direct answer to the question
            2. Relevant context supporting the answer
            3. Confidence level (High/Medium/Low)
            
            Context: {context}
            Question: {question}
            
            Format your response as:
            Answer: [your answer]
            Support: [supporting text]
            Confidence: [High/Medium/Low]
            """
        )
        
        self.question_generation_prompt = PromptTemplate(
            input_variables=["context"],
            template="""
            Generate 3 high-quality questions about the following text.
            Questions should be:
            - Clear and specific
            - Require understanding, not just recall
            - Cover different aspects of the text
            - Include question IDs (Q1, Q2, Q3)
            
            Text: {context}
            
            Format each question as:
            Q1. [question text]
            Q2. [question text]
            Q3. [question text]
            """
        )
        
        self.evaluation_prompt = PromptTemplate(
            input_variables=["context", "question", "answer"],
            template="""
            Evaluate this answer to the question based on the context:
            
            Question: {question}
            Provided Answer: {answer}
            Context: {context}
            
            Provide:
            1. Accuracy score (1-5)
            2. Explanation of the score
            3. Ideal answer
            
            Format as:
            Score: [1-5]
            Evaluation: [your evaluation]
            Ideal Answer: [suggested answer]
            """
        )
        
        # Initialize chains with error handling
        try:
            self.qa_chain = LLMChain(llm=self.llm, prompt=self.qa_prompt)
            self.question_chain = LLMChain(llm=self.llm, prompt=self.question_generation_prompt)
            self.evaluation_chain = LLMChain(llm=self.llm, prompt=self.evaluation_prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize QA chains: {str(e)}")

    def answer_question(self, text: str, question: str) -> Tuple[str, str]:
        """Answer a question based on the provided text."""
        if not text or not question:
            raise ValueError("Text and question must be provided")
            
        try:
            chunks = self._split_text(text)
            relevant_chunk = self._find_most_relevant_chunk(chunks, question)
            result = self.qa_chain.run({
                "context": relevant_chunk,
                "question": question
            })
            return self._parse_qa_response(result)
        except Exception as e:
            raise RuntimeError(f"Error answering question: {str(e)}")

  
    def generate_summary(self, text: str) -> str:
        """Generate a concise summary for the provided text."""
        if not text:
            raise ValueError("Text must be provided for summary generation")
        
        try:
            summary_prompt = PromptTemplate(
                input_variables=["context"],
                template="""
                Provide a clear, concise 5-7 sentence summary of the following academic text for a student:
                
                {context}
                
                Summary:
                """
            )
            summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
            chunks = self._split_text(text)
            main_chunk = chunks[0]
            summary = summary_chain.run({"context": main_chunk})
            return summary.strip()
        except Exception as e:
            raise RuntimeError(f"Error generating summary: {str(e)}")



    def generate_questions(self, text: str, num_questions: int = 3) -> list:
        """Generate comprehension questions from the provided text."""
        if not text:
            raise ValueError("Text must be provided for question generation")

        try:
            chunks = self._split_text(text)
            main_chunk = chunks[0]
            result = self.question_chain.run({"context": main_chunk})
            questions = self._parse_generated_questions(result)
            return questions[:num_questions]
        except Exception as e:
            raise RuntimeError(f"Error generating questions: {str(e)}")

    def evaluate_answer(self, text: str, question_id: int, answer: str) -> Dict:
        """Evaluate a user's answer to a question."""
        if not text or not answer or question_id < 0:
            raise ValueError("Invalid input parameters")
            
        try:
            questions = self.generate_questions(text)
            if question_id >= len(questions):
                return {"error": "Invalid question ID"}
                
            question = questions[question_id]
            relevant_chunk = self._find_most_relevant_chunk(self._split_text(text), question)
            
            evaluation = self.evaluation_chain.run({
                "context": relevant_chunk,
                "question": question,
                "answer": answer
            })
            
            return {
                "question": question,
                "user_answer": answer,
                "evaluation": self._parse_evaluation(evaluation)
            }
        except Exception as e:
            raise RuntimeError(f"Error evaluating answer: {str(e)}")

    # Helper methods
    def _split_text(self, text: str, chunk_size: int = 2000) -> List[str]:
        """Split text into manageable chunks."""
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def _find_most_relevant_chunk(self, chunks: List[str], question: str) -> str:
        """Find the most relevant chunk for a question (simplified)."""
        # TODO: Implement proper semantic similarity search
        return chunks[0]

    def _parse_qa_response(self, response: str) -> Tuple[str, str]:
        """Parse the QA response into answer and justification."""
        answer_match = re.search(r"Answer:\s*(.*?)\s*Support:", response, re.DOTALL)
        support_match = re.search(r"Support:\s*(.*?)\s*Confidence:", response, re.DOTALL)
        
        answer = answer_match.group(1).strip() if answer_match else "Answer not found"
        support = support_match.group(1).strip() if support_match else "Supporting context not provided"
        
        return answer, support

    def _parse_generated_questions(self, response: str) -> List[str]:
        """Parse generated questions from the LLM response."""
        questions = []
        for line in response.split('\n'):
            if line.strip() and (line.startswith('Q') or line[0].isdigit()):
                questions.append(line.strip())
        return questions[:3]  # Return at most 3 questions

    def _parse_evaluation(self, response: str) -> Dict:
        """Parse the evaluation response into structured data."""
        score_match = re.search(r"Score:\s*(\d)", response)
        eval_match = re.search(r"Evaluation:\s*(.*?)(?=Ideal Answer:|$)", response, re.DOTALL)
        ideal_match = re.search(r"Ideal Answer:\s*(.*)", response, re.DOTALL)
        
        return {
            "score": int(score_match.group(1)) if score_match else 0,
            "evaluation": eval_match.group(1).strip() if eval_match else "No evaluation provided",
            "ideal_answer": ideal_match.group(1).strip() if ideal_match else "No ideal answer provided"
        }
import json
import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Structured output schema for LLM judge
class AccuracyScore(BaseModel):
    score: float = Field(description="Accuracy score 1-5. 1=wrong, 3=acceptable, 5=perfect")
    feedback: str = Field(description="Brief explanation of the score")

class Evaluation:
    def __init__(self, config):
        self.config = config
        self.judge_llm = ChatGroq(
            model=self.config.judge_model_name,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def load_smoke_test_questions(self) -> list:
        with open(self.config.eval_set_path, 'r', encoding='utf-8') as f:
            all_questions = [json.loads(line) for line in f]
        return [all_questions[i] for i in self.config.smoke_test_questions]

    def calculate_keyword_coverage(self, keywords: list, retrieved_docs: list) -> float:
        retrieved_text = " ".join([doc.page_content.lower() for doc in retrieved_docs])
        found = sum(1 for kw in keywords if kw.lower() in retrieved_text)
        return found / len(keywords) if keywords else 0.0

    def judge_accuracy(self, question: str, generated_answer: str, reference_answer: str) -> AccuracyScore:
        judge_prompt = ChatPromptTemplate.from_template("""
You are an expert evaluator. Score the generated answer against the reference answer.

Question: {question}
Generated Answer: {generated_answer}
Reference Answer: {reference_answer}

Score accuracy 1-5:
- 1: Wrong or completely off-topic
- 3: Acceptable, partially correct  
- 5: Perfect, matches reference answer

Only give 5 for a perfect answer. If wrong, score must be 1.
""")
        structured_llm = self.judge_llm.with_structured_output(AccuracyScore)
        chain = judge_prompt | structured_llm
        return chain.invoke({
            "question": question,
            "generated_answer": generated_answer,
            "reference_answer": reference_answer
        })

    def evaluate(self, retriever, generation_component) -> dict:
        smoke_test_questions = self.load_smoke_test_questions()
        results = []

        for i, test in enumerate(smoke_test_questions):
            question = test["question"]
            reference_answer = test["reference_answer"]
            keywords = test["keywords"]

            # Retrieve ONCE — same docs used for both metrics
            retrieved_docs = retriever.invoke(question)

            # Generate
            generated_answer = generation_component.generate_response(
                query=question,
                retrieved_docs=retrieved_docs
            )

            # Score retrieval
            keyword_coverage = self.calculate_keyword_coverage(keywords, retrieved_docs)

            # Score generation
            accuracy = self.judge_accuracy(question, generated_answer, reference_answer)

            result = {
                "question": question,
                "generated_answer": generated_answer,
                "reference_answer": reference_answer,
                "keyword_coverage": keyword_coverage,
                "accuracy_score": accuracy.score,
                "feedback": accuracy.feedback,
                "retrieval_pass": keyword_coverage >= self.config.keyword_coverage_threshold,
                "generation_pass": accuracy.score >= self.config.accuracy_threshold
            }
            results.append(result)

            print(f"\nQ{i+1}: {question[:70]}...")
            print(f"Keyword Coverage: {keyword_coverage:.2f} | Accuracy: {accuracy.score}/5")
            print(f"Retrieval: {'PASS' if result['retrieval_pass'] else 'FAIL'} | Generation: {'PASS' if result['generation_pass'] else 'FAIL'}")

        # Aggregate
        avg_keyword_coverage = sum(r["keyword_coverage"] for r in results) / len(results)
        avg_accuracy = sum(r["accuracy_score"] for r in results) / len(results)

        overall_pass = (
            avg_keyword_coverage >= self.config.keyword_coverage_threshold and
            avg_accuracy >= self.config.accuracy_threshold
        )

        print(f"\n{'='*50}")
        print(f"FINAL RESULTS")
        print(f"Avg Keyword Coverage: {avg_keyword_coverage:.3f} (threshold: {self.config.keyword_coverage_threshold})")
        print(f"Avg Accuracy: {avg_accuracy:.3f} (threshold: {self.config.accuracy_threshold})")
        print(f"OVERALL: {'PASS ✓' if overall_pass else 'FAIL ✗'}")
        print(f"{'='*50}")

        return {
            "results": results,
            "avg_keyword_coverage": avg_keyword_coverage,
            "avg_accuracy": avg_accuracy,
            "overall_pass": overall_pass
        }
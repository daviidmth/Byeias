import re
import sys
from pathlib import Path


def _add_src_to_path():
    from pathlib import Path
    import sys
    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents]
    for candidate in candidates:
        src_path = candidate / "src"
        package_path = src_path / "byeias"
        if package_path.exists():
            src_str = str(src_path)
            if src_str not in sys.path:
                sys.path.insert(0, src_str)
            return src_path
    raise RuntimeError("Could not find 'src' directory in current or parent paths. Ensure you are running this script from within the project directory structure.")
_add_src_to_path()


from byeias.backend.classification.model_bias import BiasDetectionPipeline
from byeias.backend.extraction.text_extracter import PDFTextExtractor
from byeias.backend.llm_explanation.llm_communicator import LLMCommunicator
from byeias.backend.classification.model_bias import BiasDetectionPipeline
from byeias.backend.config_loader import get_backend_config

class BackendController:
    """
    Zentrale Steuerung für das Backend: Klassifikation, PDF-Extraktion, LLM-Kommunikation.
    """

    def __init__(self, model_name=None, device=None, llm_model=None, llm_api_key=None):
        self.classifier = BiasDetectionPipeline(model_name=model_name, device=device)
        self.pdf_extractor = PDFTextExtractor(language="german")
        self.llm = LLMCommunicator(model_name=llm_model, api_key=llm_api_key)
        self.config = get_backend_config()


    def process_data(self, input_text):
        raw_sentences = re.split(r'(?<=[.!?])\s+', input_text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        print(f"Eingabetext in {len(sentences)} Sätze aufgeteilt.")

        if not sentences:
            print("Keine Sätze zum Verarbeiten gefunden.")
            return []

        pipeline = BiasDetectionPipeline(model_name=self.config.classification.model_name)
        llm = LLMCommunicator()

        context_texts = []
        target_texts = []
        contexts_before = []
        contexts_after = []

        for i in range(len(sentences)):
            target = sentences[i]
            
            before = sentences[i-1] if i > 0 else ""
            
            after = sentences[i+1] if i + 1 < len(sentences) else ""
            
            combined_context = f"{before} {after}".strip()
            
            target_texts.append(target)
            context_texts.append(combined_context)
            
            contexts_before.append(before)
            contexts_after.append(after)

        print("Starte Vorhersage für alle Sätze...")
        inference_results = pipeline.predict(
            context_texts=context_texts, 
            target_texts=target_texts
        )

        print("Inferenz-Ergebnisse:", inference_results)

        explanations = []

        for i, result in enumerate(inference_results):
            if result["sexism_prediction"] == 1 or result["racism_prediction"] == 1:
                print(f"\n[BIAS GEFUNDEN] in Satz {i+1}: '{result['text']}'")
                
                explanation = llm.explain_bias(
                    context_before=contexts_before[i],
                    flagged_sentence=result["text"],
                    context_after=contexts_after[i],
                )
                
                explanations.append({
                    "satz_index": i + 1,
                    "geflaggter_satz": result["text"],
                    "bias_typ": "Sexismus" if result["sexism_prediction"] == 1 else "Rassismus",
                    "llm_erklaerung": explanation
                })

        return explanations

    # --- Klassifikation ---
    def train_classifier(self, **kwargs):
        return self.classifier.train(**kwargs)

    def predict_bias(self, context_texts, target_texts):
        return self.classifier.predict(
            context_texts=context_texts, target_texts=target_texts
        )

    # --- PDF-Extraktion ---
    def extract_pdf_sentences(self, pdf_path):
        return self.pdf_extractor.extract_sentences(pdf_path)

    # --- LLM-Kommunikation ---
    def explain_bias(self, context_before, flagged_sentence, context_after):
        return self.llm.explain_bias(context_before, flagged_sentence, context_after)


if __name__ == "__main__":
    text = "The Topic is about payment. Girls get paid less. The teacher explained the next task. Everyone was listening."
    ergebnisse = BackendController().process_data(text)


    print("\n--- FINALE ZUSAMMENFASSUNG ---")
    for erg in ergebnisse:
        print(f"Satz {erg['satz_index']} ({erg['bias_typ']}): {erg['geflaggter_satz']}")
        print(f"Erklärung: {erg['llm_erklaerung']}\n")
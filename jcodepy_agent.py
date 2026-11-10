import json
import math
import os
import re
import tempfile
from pathlib import Path


class JCodePyAgentCore:
    """Local FAQ retrieval and calculator; not a generative model or AGI."""

    DEFAULT_KNOWLEDGE = {
        "greetings": ["Hello. The local JCodePy memory helper is ready."],
        "facts": [
            "WiCi One serves model requests on the local network.",
            "Keep API keys and device tokens in environment variables; never commit them.",
            "This helper retrieves saved text and does not invent answers.",
        ],
    }

    def __init__(self, similarity_threshold=0.6, kb_path="_base.json"):
        self.similarity_threshold = float(similarity_threshold)
        if not 0 <= self.similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1")
        self.kb_path = Path(kb_path)
        self.knowledge_base = {}
        self.load_knowledge_base()

    def load_knowledge_base(self):
        try:
            data = json.loads(self.kb_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or any(
                not isinstance(category, str) or not isinstance(entries, list)
                or any(not isinstance(entry, str) for entry in entries)
                for category, entries in data.items()
            ):
                raise ValueError("Knowledge base must map categories to lists of strings")
            self.knowledge_base = data
        except FileNotFoundError:
            self.knowledge_base = {key: list(value) for key, value in self.DEFAULT_KNOWLEDGE.items()}
            self.save_knowledge_base()
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in knowledge base: {self.kb_path}") from exc

    def save_knowledge_base(self):
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(dir=self.kb_path.parent, prefix=".knowledge-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(self.knowledge_base, file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temporary_name, self.kb_path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)

    @staticmethod
    def tokenize(text):
        return set(re.findall(r"[\w'-]+", str(text).casefold(), flags=re.UNICODE))

    @classmethod
    def compute_cosine_similarity(cls, text1, text2):
        tokens1, tokens2 = cls.tokenize(text1), cls.tokenize(text2)
        if not tokens1 or not tokens2:
            return 0.0
        return len(tokens1 & tokens2) / math.sqrt(len(tokens1) * len(tokens2))

    def evaluate_memory(self, probe_string):
        candidates = [
            (category, text, self.compute_cosine_similarity(probe_string, text))
            for category, entries in self.knowledge_base.items() for text in entries
        ]
        if not candidates:
            return None, 0.0
        best = max(candidates, key=lambda candidate: candidate[2])
        return best, best[2]

    def respond_to(self, message):
        best, score = self.evaluate_memory(message)
        if best and score >= self.similarity_threshold:
            return best[1]
        return "No sufficiently similar saved answer was found. Ask a configured model provider or add a reviewed knowledge-base entry."

    def add_entry(self, category, text):
        if not isinstance(category, str) or not category.strip() or not isinstance(text, str) or not text.strip():
            raise ValueError("Category and text must be non-empty strings")
        entries = self.knowledge_base.setdefault(category.strip(), [])
        if text not in entries:
            entries.append(text)
            self.save_knowledge_base()

    @staticmethod
    def kalkul8_dual_volume_analysis(length_a, width_a, height_a, length_b, width_b, height_b):
        dims = [float(value) for value in (length_a, width_a, height_a, length_b, width_b, height_b)]
        if any(not math.isfinite(value) or value < 0 for value in dims):
            raise ValueError("Dimensions must be finite, non-negative numbers")
        la, wa, ha, lb, wb, hb = dims
        vol_a, vol_b = la * wa * ha, lb * wb * hb
        return {
            "volume_box_a": vol_a,
            "volume_box_b": vol_b,
            "surface_box_a": 2 * (la * wa + wa * ha + ha * la),
            "surface_box_b": 2 * (lb * wb + wb * hb + hb * lb),
            "ratio_a_to_b": vol_a / vol_b if vol_b else None,
            "volumetric_variance": abs(vol_a - vol_b),
        }


if __name__ == "__main__":
    agent = JCodePyAgentCore(kb_path=os.environ.get("WICI_KB_PATH", "_base.json"))
    print("JCodePy local memory helper (not a generative model). Type 'exit' to quit.")
    try:
        while True:
            message = input("You> ").strip()
            if message.casefold() in {"exit", "quit"}:
                break
            if message:
                print(f"Memory> {agent.respond_to(message)}")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")

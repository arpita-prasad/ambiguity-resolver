"""
server.py
=========
FastAPI backend for ArthaBot.
Loads the trained transformer from ./saved_model/ and serves predictions.

Run: python server.py
API: http://localhost:8000
"""

import json
import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import BertTokenizer, BertForSequenceClassification
import os

# Config
MODEL_PATH = "saved_model"
MAX_LEN    = 128
THRESHOLD  = 0.35 
NUM_LABELS = 8

# Full metadata for each ambiguity type
AMBIGUITY_META = {
    "LEXICAL AMBIGUITY": {
        "category": "Word-level",
        "description": "A word in the sentence has multiple possible meanings (polysemy or homonymy). The correct meaning cannot be determined without broader context.",
        "nlp_concept": "Polysemy / Homonymy"
    },
    "SYNTACTIC AMBIGUITY": {
        "category": "Structure-level",
        "description": "The grammatical structure of the sentence can be parsed in more than one way, leading to different interpretations.",
        "nlp_concept": "Attachment ambiguity / Coordination ambiguity"
    },
    "SEMANTIC AMBIGUITY": {
        "category": "Meaning-level",
        "description": "The meaning of a phrase is unclear even when the sentence structure is unambiguous. Often arises from metaphor or figurative language.",
        "nlp_concept": "Quantifier scope / Figurative meaning"
    },
    "PRAGMATIC AMBIGUITY": {
        "category": "Context-level",
        "description": "The intended meaning of the utterance differs based on context, speaker intent, or the speech act being performed.",
        "nlp_concept": "Speech act theory / Implicature"
    },
    "REFERENTIAL AMBIGUITY": {
        "category": "Reference-level",
        "description": "A pronoun or noun phrase can refer to more than one entity in the discourse, making it unclear who or what is being discussed.",
        "nlp_concept": "Coreference resolution / Anaphora"
    },
    "SCOPE AMBIGUITY": {
        "category": "Operator-level",
        "description": "Operators like negation ('नहीं') or quantifiers ('सब', 'कोई') can take different scopes over the sentence, yielding different truth conditions.",
        "nlp_concept": "Negation scope / Quantifier scope"
    },
    "PHONOLOGICAL AMBIGUITY": {
        "category": "Sound-level",
        "description": "Two different words or meanings share the same or similar phonological form. Especially relevant in transliterated Hinglish where spelling does not distinguish sounds.",
        "nlp_concept": "Homophony / Transliteration ambiguity"
    },
    "MORPHOLOGICAL AMBIGUITY": {
        "category": "Word-form-level",
        "description": "A word form can be analyzed with multiple morphological structures or grammatical categories (e.g., same form as noun and verb).",
        "nlp_concept": "POS ambiguity / Morphological analysis"
    },
}

# Load model
print("Loading model from", MODEL_PATH)
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(
        f"Model not found at '{MODEL_PATH}'. "
        "Please run: python train_model.py"
    )

tokenizer   = BertTokenizer.from_pretrained(MODEL_PATH)
model       = BertForSequenceClassification.from_pretrained(MODEL_PATH)
device      = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

with open(os.path.join(MODEL_PATH, "label_names.json")) as f:
    LABEL_NAMES = json.load(f)

print(f"✓ Model loaded on {device}")
print(f"✓ Labels: {LABEL_NAMES}")

# App
app = FastAPI(
    title="ArthaBot API",
    description="Hindi/Hinglish Ambiguity Detection using Transformer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    sentence: str


def detect_language(sentence: str) -> str:
    """Simple heuristic to detect language."""
    devanagari_chars = sum(1 for c in sentence if '\u0900' <= c <= '\u097F')
    total_alpha      = sum(1 for c in sentence if c.isalpha())
    if total_alpha == 0:
        return "Hindi"
    ratio = devanagari_chars / total_alpha
    if ratio > 0.7:
        return "Hindi"
    elif ratio > 0.1:
        return "Hinglish"
    else:
        return "Hinglish"


def generate_meanings_and_resolution(sentence: str, detected_types: list) -> tuple:
    """
    Rule-based meaning generation based on detected ambiguity types.
    In a more advanced system this would use a generative model.
    """
    meanings = []
    resolution = ""

    if not detected_types:
        meanings = [{
            "meaning_number": 1,
            "interpretation": sentence,
            "explanation": "This sentence appears to have a single clear interpretation with no detected ambiguity.",
            "context_clue": "No additional context needed."
        }]
        resolution = "The sentence is unambiguous and can be interpreted at face value."
        return meanings, resolution

    type_set = [t["type"] for t in detected_types]

    if "LEXICAL AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Interpretation A: Using the primary/most common word meaning",
                "explanation": "The ambiguous word is interpreted with its most frequent meaning in everyday Hindi usage.",
                "context_clue": "More context about the topic would resolve this."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Interpretation B: Using the secondary word meaning",
                "explanation": "The ambiguous word is interpreted with its alternate meaning, which is equally grammatically valid.",
                "context_clue": "Domain or situational context would disambiguate."
            }
        ])
        resolution = "Most likely the primary/common word meaning applies in everyday conversation."

    if "SYNTACTIC AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Parse A: Grouping the first constituent together",
                "explanation": "Under this parse, the modifier/clause attaches to the nearest noun phrase.",
                "context_clue": "Prosody or punctuation in spoken/written form would clarify."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Parse B: Grouping across a wider constituent",
                "explanation": "Under this parse, the modifier/clause attaches to the broader noun phrase.",
                "context_clue": "The speaker's intended reference would resolve this."
            }
        ])
        resolution = "Default: closest attachment (minimal attachment principle) is the most common parse."

    if "PRAGMATIC AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Direct speech act: literal meaning of the utterance",
                "explanation": "The utterance is taken at face value as a statement, question, or command.",
                "context_clue": "Neutral conversational context."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Indirect speech act: implied/contextual meaning",
                "explanation": "The utterance carries an indirect meaning based on shared context or social norms.",
                "context_clue": "Tone, relationship, and situational context determine the actual intent."
            }
        ])
        resolution = "Context and speaker intent are required to determine the pragmatic meaning."

    if "REFERENTIAL AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Referent A: pronoun refers to the most recently mentioned entity",
                "explanation": "Following the recency principle in discourse, the pronoun refers to the entity most recently introduced.",
                "context_clue": "Prior discourse context establishes the referent."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Referent B: pronoun refers to the topic entity",
                "explanation": "The pronoun refers to the main topic of the discourse, which may have been mentioned earlier.",
                "context_clue": "Topic continuity in the conversation clarifies reference."
            }
        ])
        resolution = "Coreference is typically resolved by prior discourse — the most salient entity is usually the referent."

    if "SCOPE AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Wide scope: operator takes scope over entire sentence",
                "explanation": "The negation or quantifier applies broadly to the entire predicate.",
                "context_clue": "Stress and intonation in speech clarify scope."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Narrow scope: operator takes scope over only a sub-phrase",
                "explanation": "The negation or quantifier applies only to a specific constituent.",
                "context_clue": "Context about what is being denied or quantified resolves this."
            }
        ])
        resolution = "Narrow scope (negation over the predicate) is the default interpretation in Hindi."

    if "SEMANTIC AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Literal reading: words taken at their dictionary meaning",
                "explanation": "Every word contributes its literal, compositional meaning.",
                "context_clue": "A very formal or technical context would favor literal reading."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Figurative/idiomatic reading: metaphorical or conventional meaning",
                "explanation": "The phrase is understood as a conventional metaphor or idiom rather than literally.",
                "context_clue": "Everyday conversational context favors the figurative reading."
            }
        ])
        resolution = "The figurative/idiomatic reading is almost always intended in natural conversation."

    if "PHONOLOGICAL AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Sound interpretation A: neutral/polite meaning",
                "explanation": "The word is interpreted as the neutral, commonly intended meaning in polite speech.",
                "context_clue": "Formal or neutral conversational register."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Sound interpretation B: alternate phonological reading",
                "explanation": "The same sound can map to a different word with a very different meaning in Hindi/Urdu phonology.",
                "context_clue": "Spelling in Devanagari script would remove this ambiguity."
            }
        ])
        resolution = "The neutral meaning is intended in polite contexts. Written Devanagari resolves phonological ambiguity."

    if "MORPHOLOGICAL AMBIGUITY" in type_set:
        meanings.extend([
            {
                "meaning_number": len(meanings) + 1,
                "interpretation": "Morphological reading A: primary grammatical category",
                "explanation": "The word form is analyzed as its most common part of speech (e.g., verb).",
                "context_clue": "Surrounding syntax usually determines the POS."
            },
            {
                "meaning_number": len(meanings) + 2,
                "interpretation": "Morphological reading B: secondary grammatical category",
                "explanation": "The same word form can also be analyzed as a different part of speech (e.g., noun).",
                "context_clue": "Sentence position and surrounding words resolve morphological ambiguity."
            }
        ])
        resolution = "Syntactic context (surrounding words) typically resolves morphological ambiguity."

    # Deduplicate meaning numbers
    for i, m in enumerate(meanings):
        m["meaning_number"] = i + 1

    return meanings, resolution


@app.get("/")
def root():
    return {
        "name": "ArthaBot API",
        "status": "running",
        "model": "bert-base-multilingual-cased (fine-tuned)",
        "task": "Hindi/Hinglish Ambiguity Detection",
        "labels": LABEL_NAMES
    }


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    sentence = req.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail="Sentence cannot be empty.")

    # Tokenize
    encoding = tokenizer(
        sentence,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    input_ids      = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    # Inference
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits  = outputs.logits
        probs   = torch.sigmoid(logits).cpu().numpy()[0]

    # Build detected ambiguities
    detected = []
    for i, (label, prob) in enumerate(zip(LABEL_NAMES, probs)):
        if prob >= THRESHOLD:
            meta     = AMBIGUITY_META[label]
            severity = "high" if prob >= 0.7 else "medium" if prob >= 0.5 else "low"
            detected.append({
                "type":                 label,
                "category":             meta["category"],
                "explanation":          meta["description"],
                "example_from_sentence": sentence,
                "severity":             severity,
                "confidence_score":     round(float(prob), 4),
                "nlp_concept":          meta["nlp_concept"]
            })

    # Sort by confidence
    detected.sort(key=lambda x: x["confidence_score"], reverse=True)

    # Meanings + resolution
    meanings, resolution = generate_meanings_and_resolution(sentence, detected)

    # Overall confidence
    max_prob = float(max(probs)) if len(probs) > 0 else 0.0
    if max_prob >= 0.7:
        confidence = "high"
    elif max_prob >= 0.45:
        confidence = "medium"
    else:
        confidence = "low"

    # Linguistic note
    if detected:
        types_str = ", ".join(d["type"].split()[0].capitalize() for d in detected)
        note = (
            f"This sentence exhibits {types_str} ambiguity — "
            f"a well-studied phenomenon in Hindi/Hinglish NLP. "
            f"The ambiguity arises from the structural and lexical properties of Hindi, "
            f"which is a pro-drop, SOV language with rich morphology. "
            f"Resolving such ambiguity typically requires discourse context, prosodic cues, or world knowledge."
        )
    else:
        note = (
            "This sentence appears to be unambiguous. "
            "It has a single clear syntactic parse, unambiguous word meanings, "
            "and clear referential structure in isolation."
        )

    return {
        "original_sentence":  sentence,
        "language_detected":  detect_language(sentence),
        "ambiguity_found":    len(detected) > 0,
        "ambiguities":        detected,
        "possible_meanings":  meanings,
        "resolved_most_likely": resolution,
        "confidence":         confidence,
        "linguistic_note":    note,
        "model_info": {
            "name":        "bert-base-multilingual-cased",
            "task":        "multi-label classification",
            "num_labels":  NUM_LABELS,
            "threshold":   THRESHOLD
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
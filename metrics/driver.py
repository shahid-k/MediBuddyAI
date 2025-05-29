# example_driver.py
from readability import flesch_reading_ease
from bart_score import bert_score
from perplexity import perplexities
from emotional_vader import vader_scores
from rouge_metric import rouge

system_output = """
Symptoms:
Diarrhea
Hypotension
Occasional Dizziness

Possible Causes:
Viral gastroenteritis (stomach flu)
Food poisoning
Dehydration from excessive sweating or inadequate fluid intake

Recommended Next Steps:
Drink plenty of fluids to stay hydrated (water, clear broths, electrolyte-rich drinks like sports drinks)
Rest and avoid strenuous activities until symptoms improve
Eat small, frequent meals of bland foods (bananas, rice, applesauce, toast) to help settle the stomach
Consider over-the-counter anti-diarrheal medication if symptoms persist or worsen (consult a pharmacist for guidance)
Seek medical attention if symptoms worsen or persist for more than a few days, or if there are signs of dehydration (excessive thirst, dark urine, dizziness)
Urgency Rating: 3
"""
reference_text = """
Symptoms:
Diarrhea
Hypotension
Increased white blood cell count

Possible Causes:
Long-standing hypertension
Polycystic kidney disease
Recurrent kidney infections

Recommended Next Steps:
Schedule an urgent consultation with a nephrologist
Begin evaluation and preparation for dialysis or kidney transplantation
Follow a renal diet (low sodium, potassium, and phosphorus)
Regularly monitor fluid intake and output
Undergo routine blood tests to assess kidney function and manage complications (anemia, bone health, electrolyte disturbances)
Seek immediate medical attention if experiencing chest pain, severe shortness of breath, or confusion

Urgency Rating: 3
"""

print("Flesch Reading-Ease:", flesch_reading_ease(system_output))
print("VADER Score:", vader_scores(system_output))
print("ROUGE Score:", rouge([system_output], [reference_text]))
print("Perplexity Score:", perplexities([system_output], model_id="gpt2")[0])
print("BERTScore F1:", bert_score(system_output, reference_text))

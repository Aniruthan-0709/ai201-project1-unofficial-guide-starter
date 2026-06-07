from generator import generate_response
from retrieve import embed_and_store

embed_and_store()

questions = [
    {
        "q": "What physiological mechanism causes airway narrowing during an asthma attack?",
        "expected": "Bronchoconstriction from smooth muscle contraction, mucus production, and airway inflammation"
    },
    {
        "q": "How does exercise-induced bronchoconstriction differ from classical asthma?",
        "expected": "EIB is triggered by physical exertion and airway cooling/drying, not allergens; can occur in people without chronic asthma"
    },
    {
        "q": "What is the difference between a rescue inhaler and a controller medication?",
        "expected": "Rescue inhalers (SABAs) give immediate relief; controllers (inhaled corticosteroids) reduce inflammation daily and prevent attacks"
    },
    {
        "q": "What occupational exposures are known to cause occupational asthma?",
        "expected": "Isocyanates, flour dust, latex, animal proteins, and wood dust"
    },
    {
        "q": "How is a peak flow meter used to monitor asthma severity?",
        "expected": "Measures peak expiratory flow rate; compared to personal best to detect worsening before symptoms appear"
    }
]

for i, item in enumerate(questions, 1):
    print(f"\n{'='*70}")
    print(f"Q{i}: {item['q']}")
    print(f"Expected: {item['expected']}")
    print('='*70)
    result = generate_response(item["q"])
    print(f"System answer:\n{result['answer']}\n")
    print(f"Retrieved from: {', '.join(result['sources'])}")
    
    # Show retrieved chunk quality
    print(f"\nTop retrieved chunk (distance {result['chunks'][0]['distance']:.4f}):")
    print(f"  Source: {result['chunks'][0]['source']}")
    print(f"  Text: {result['chunks'][0]['text'][:200]}...")